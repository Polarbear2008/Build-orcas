# Day 2: AirCanvas

## Description
A virtual whiteboard that lets you draw in the air using your fingers! Just hold up your hand to the webcam, pinch your index finger and thumb together to draw on the screen. Release your pinch to lift the pen.

## Tech Stack
- OpenCV
- MediaPipe Hands

## Setup
Ensure you have installed the global dependencies via the root `requirements.txt`.
```bash
# In the root of the repository
source .venv/bin/activate
cd days/day-02-aircanvas
python aircanvas.py
```

## Features
- **Pinch to Draw**: Pinch index and thumb to draw.
- **Change Colors**: Press `c` to cycle through colors.
- **Undo**: Press `z` to undo your last stroke.
- **Clear Canvas**: Press `x` to erase everything.
