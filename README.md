# Rock, Paper, Scissors — Hand Tracking

A webcam-based Rock, Paper, Scissors game built as a learning project for **OpenCV** and **MediaPipe**. It uses MediaPipe's hand-landmark model to detect a hand, classifies the pose as rock, paper, or scissors, and displays the game in a live OpenCV window.

## Features

- Detects one hand from your webcam using MediaPipe Hand Landmarker.
- Draws the 21 hand landmarks and their connections with OpenCV.
- Classifies the following gestures:
  - **Rock** — closed fist
  - **Paper** — open hand
  - **Scissors** — index and middle fingers extended
- Runs a Rock → Paper → Scissors → Shoot countdown, chooses a computer move, and shows the round result.
- Press `q` to quit.

## Requirements

- Python 3.10 or newer
- A working webcam
- Permission for your terminal or IDE to access the camera

The MediaPipe model required by the app is included at `tasks/hand_landmarker.task`.

## Setup

1. Clone the repository and enter the project directory.

   ```bash
   git clone <repository-url>
   cd Rock_Paper_Scissors_Spock_Lizard
   ```

2. Create and activate a virtual environment.

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   On Windows PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

3. Install the dependencies.

   ```bash
   pip install -r requirements.txt
   ```

## Run the game

```bash
python main.py
```

An OpenCV window opens with the live camera feed. Hold a hand in view to start a round, make your gesture when **SHOOT!** appears, then wait for the result. After the short cooldown, show your hand again to play another round.

## Project structure

```text
.
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── tasks/
│   └── hand_landmarker.task   # MediaPipe hand-landmark model
└── rps/
    ├── gestureClassifier.py   # Converts landmarks into game gestures
    ├── rps.py                 # Game rules and winner selection
    └── showcam.py             # Webcam capture, detection, and display loop
```

## How gesture recognition works

MediaPipe returns 21 normalized landmarks for the detected hand. The classifier compares each fingertip's distance from the wrist with a joint lower on the same finger:

- all fingers curled → rock
- all fingers extended → paper
- index and middle extended, ring and pinky curled → scissors

Other hand poses are treated as unrecognized so they do not count as a valid move.

## Learning goals

This project is intended for experimenting with:

- camera capture and drawing overlays with OpenCV;
- hand landmark detection with MediaPipe Tasks;
- translating landmark coordinates into gesture rules; and
- managing interactive application state with a simple game loop.

## Troubleshooting

- **Camera does not open:** Confirm no other application is using it and grant camera access to the terminal or IDE.
- **No hand is detected:** Improve lighting, keep your hand fully in frame, and face your palm toward the camera.
- **Module import errors:** Make sure the virtual environment is active and reinstall with `pip install -r requirements.txt`.

## License

No license has been specified for this repository.
