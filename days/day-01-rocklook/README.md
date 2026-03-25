# RockLook

Detect when you look away or downward via webcam. It triggers rock music playback when your gaze drops or shifts away from the screen, meaning you aren't paying attention. Looking up pauses it.

## Hardware Concept Analog
Sensor -> threshold -> actuator. This mirrors a physical tilt sensor (tracking head angle) triggering an electrical relay (audio script).

## Tech Stack
- OpenCV
- MediaPipe FaceMesh
- Pygame Mixer

## Setup
python3 -m venv venv
source venv/bin/activate
pip install opencv-python mediapipe pygame

Run the program:
python rocklook.py

Your terminal will request permission to access your Mac camera. Once permitted, a window appears displaying your live camera feed. Threshold values are displayed directly on the video feed.
