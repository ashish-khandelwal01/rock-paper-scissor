import os
import cv2
import mediapipe as mp
import time
import sys

from rps.gestureClassifier import classify_gesture
from rps.rps import select_winner

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# The 21 hand landmarks are connected in this order to form the "skeleton".
# This used to live inside mp.solutions.hands.HAND_CONNECTIONS - since that
# module is gone, we just hardcode the same pairs here.
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),          # index finger
    (5, 9), (9, 10), (10, 11), (11, 12),     # middle finger
    (9, 13), (13, 14), (14, 15), (15, 16),   # ring finger
    (13, 17), (17, 18), (18, 19), (19, 20),  # pinky
    (0, 17)                                  # palm base
]

# The classic countdown cadence, each word shown for this many seconds.
COUNTDOWN_WORDS = ["Rock...", "Paper...", "Scissors...", "SHOOT!"]
SECONDS_PER_WORD = 0.7

# How long a hand must be continuously visible before we trust it's really
# there (not just a one-frame flicker/false detection) and start the countdown.
HAND_PRESENCE_DEBOUNCE = 0.3

# How long to pause after a round before we're willing to start a new one.
COOLDOWN_SECONDS = 2.5

# The three states this loop can be in.
STATE_IDLE = "idle"
STATE_COUNTDOWN = "countdown"
STATE_COOLDOWN = "cooldown"

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        # Running inside the packaged app
        base = os.path.abspath(os.path.join(os.path.dirname(sys.executable), "..", "Resources", "app"))
    else:
        # Running from normal Python / PyCharm
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)

def draw_landmarks(frame, hand_landmarks_list):
    h, w, _ = frame.shape
    for hand_landmarks in hand_landmarks_list:
        # convert normalized (0-1) coords to pixel coords
        points = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]

        for start_idx, end_idx in HAND_CONNECTIONS:
            cv2.line(frame, points[start_idx], points[end_idx], (0, 255, 0), 2)

        for point in points:
            cv2.circle(frame, point, 4, (0, 0, 255), -1)


def capture_screen():
    options = HandLandmarkerOptions(
        base_options=BaseOptions(
            model_asset_path=resource_path(os.path.join("tasks", "hand_landmarker.task")),
            delegate=BaseOptions.Delegate.CPU  # ← force CPU
        ),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    landmarker = HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(0)
    start_time = time.time()
    current_gesture = None  # whatever gesture is showing right now, updated every frame

    state = STATE_IDLE
    hand_first_seen_at = None    # when the hand appeared continuously, during IDLE
    countdown_start_time = None
    last_word_index = -1
    cooldown_start_time = None
    last_round_message = ""  # what to display throughout the cooldown period

    while True:
        success, frame = cap.read()

        if not success:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # VIDEO mode needs a strictly increasing timestamp in milliseconds
        timestamp_ms = int((time.time() - start_time) * 1000)

        result = landmarker.detect_for_video(mp_image, timestamp_ms)
        current_gesture = None
        hand_present = bool(result.hand_landmarks)

        if hand_present:
            draw_landmarks(frame, result.hand_landmarks)
            landmarks = result.hand_landmarks[0]
            current_gesture = classify_gesture(landmarks)

        # --- state machine ---

        if state == STATE_IDLE:
            cv2.putText(frame, "Show your hand to play!", (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)

            if hand_present:
                if hand_first_seen_at is None:
                    hand_first_seen_at = time.time()
                elif time.time() - hand_first_seen_at >= HAND_PRESENCE_DEBOUNCE:
                    # hand has been steadily visible for long enough - start playing
                    state = STATE_COUNTDOWN
                    countdown_start_time = time.time()
                    last_word_index = -1
                    hand_first_seen_at = None
            else:
                # hand disappeared before the debounce finished - reset the timer
                hand_first_seen_at = None

        elif state == STATE_COUNTDOWN:
            elapsed = time.time() - countdown_start_time
            word_index = int(elapsed / SECONDS_PER_WORD)

            if word_index < len(COUNTDOWN_WORDS):
                cv2.putText(frame, COUNTDOWN_WORDS[word_index], (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 140, 255), 4)

                if word_index == len(COUNTDOWN_WORDS) - 1 and word_index != last_word_index:
                    # this is the single frame where we just hit "SHOOT!" - lock in the guess
                    if current_gesture:
                        winner = select_winner(current_gesture)

                        messages = {
                            "win": "You won!",
                            "lose": "Computer won!",
                            "tie": "It's a tie!"
                        }
                        last_round_message = messages.get(winner, "Invalid hand gesture - try again")
                    else:
                        last_round_message = "No gesture detected - try again"

                    state = STATE_COOLDOWN
                    cooldown_start_time = time.time()

                last_word_index = word_index

        elif state == STATE_COOLDOWN:
            cv2.putText(frame, last_round_message, (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2.3, (139, 105, 20), 2)
            cv2.putText(frame, "Show your hand again to replay", (20, 95),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

            if time.time() - cooldown_start_time >= COOLDOWN_SECONDS:
                state = STATE_IDLE
                hand_first_seen_at = None

        # show the live-detected gesture as a small overlay so you get instant feedback
        display_text = current_gesture if current_gesture else "..."
        cv2.putText(frame, display_text, (20, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX,
                    0.9, (255, 255, 0), 2)
        cv2.putText(frame, "q = quit", (20, frame.shape[0] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow("Hand Tracking", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    landmarker.close()
    cap.release()
    cv2.destroyAllWindows()
