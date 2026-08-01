"""
Converts a single hand's 21 landmarks into a rock/paper/scissor label.

Detection method: for each finger, compare how far its FINGERTIP is from the
wrist versus how far a REFERENCE JOINT partway down that same finger is from
the wrist. If the tip is farther from the wrist than the reference joint,
the finger is straightened out and away from the palm (extended). If the
tip is closer to the wrist than the reference joint, the finger has folded
back toward the palm (curled).

This is the same check applied identically to all 5 fingers, including the
thumb - no separate x/y logic, no handedness, no assumption about which way
the hand is facing. It only cares about relative distance, so it holds up
whether your hand is tilted, rotated, or at an angle to the camera.
"""

import math

WRIST = 0

# (tip_landmark, reference_joint_landmark) for each finger.
# For the thumb we use the IP joint (3) as the reference - the thumb's
# equivalent of a PIP joint on the other fingers.
FINGER_JOINTS = {
    "thumb": (4, 3),
    "index": (8, 6),
    "middle": (12, 10),
    "ring": (16, 14),
    "pinky": (20, 18),
}


def _distance(point_a, point_b):
    """Straight-line distance between two landmarks (x/y only - z from
    mediapipe is depth-estimated and noisier, so we skip it)."""
    return math.hypot(point_a.x - point_b.x, point_a.y - point_b.y)


def _finger_extended(landmarks, tip_idx, ref_idx):
    wrist = landmarks[WRIST]
    tip_dist = _distance(landmarks[tip_idx], wrist)
    ref_dist = _distance(landmarks[ref_idx], wrist)
    return tip_dist > ref_dist


def get_finger_states(landmarks):
    """Returns a dict of which fingers are currently extended."""
    return {
        name: _finger_extended(landmarks, tip_idx, ref_idx)
        for name, (tip_idx, ref_idx) in FINGER_JOINTS.items()
    }


def classify_gesture(landmarks):
    """Returns 'rock', 'paper', 'scissor', or None if the pose doesn't match any of them."""
    fingers = get_finger_states(landmarks)
    extended_count = sum(fingers.values())

    if extended_count == 0:
        return "rock"

    if extended_count == 5:
        return "paper"

    if fingers["index"] and fingers["middle"] and not fingers["ring"] and not fingers["pinky"]:
        return "scissor"

    return None