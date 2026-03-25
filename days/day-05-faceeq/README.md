# FaceEQ

Turn your head left and right to scrub (fast-forward or rewind) through a song. Tilt your head left or right to dynamically alter the pitch playback.

## Hardware Concept Analog
Acoustic Actuator + IMU. Simulating a mechanical vinyl turntable combined with an accelerometer; head rotation acts as the physical jog wheel (scrubbing playback indices), while head tilt adjusts the spindle motor RPMs (resampling data frames over time affecting pitch/speed).

## Tech Stack
- OpenCV + MediaPipe
- Scipy
- Sounddevice

## Setup
Ensure you have installed the global packages (`pip install -r requirements.txt`). 
```bash
source ../../.venv/bin/activate
cd days/day-05-faceeq
python faceeq.py
```
Face forward to listen at regular speed. Look hard right to fast forward. Look hard left to rewind. Tilt head to warp pitch.
