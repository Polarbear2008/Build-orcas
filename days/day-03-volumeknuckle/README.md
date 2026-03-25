# Day 3: VolumeKnuckle

## Description
Control your Mac's system volume using nothing but your fist. Show your fist to the webcam and raise it to increase the volume or lower it to decrease the volume.

## Tech Stack
- OpenCV
- MediaPipe Hands

## Setup
Ensure you have installed the global dependencies via the root `requirements.txt`.
```bash
# In the root of the repository
source .venv/bin/activate
cd days/day-03-volumeknuckle
python volumeknuckle.py
```

## Features
- **Fist Detection**: Recognises when all four fingers are curled down toward the palm.
- **Volume Control**: Native macOS integration using `osascript`.
- **Live GUI**: Displays the real-time volume bar and instructions overlaid on your webcam feed.
