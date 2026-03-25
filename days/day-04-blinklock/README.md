# Day 4: BlinkLock

## Description
A simulated lock screen triggered by your blink patterns. Blink rapidly three times within 2.5 seconds to lock the screen. To unlock it, give a deliberate wink (one eye closed, one eye open).

## Tech Stack
- OpenCV
- MediaPipe FaceMesh
- Numpy

## Setup
Ensure you have installed the global dependencies via the root `requirements.txt`.
```bash
# In the root of the repository
source .venv/bin/activate
cd days/day-04-blinklock
python blinklock.py
```

## Features
- **Eye Aspect Ratio Extraction**: Calculates the precise opening of both eyes simultaneously.
- **Temporal Event Tracking**: Stores blink timestamps to detect rapid succession locking triggers.
- **Asymmetric Confidence**: Winking logic guarantees you can't accidentally unlock it by simply blinking again.
