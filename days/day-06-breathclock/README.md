# BreathClock

Listens to your microphone to track your breathing and calculate your Breaths Per Minute (BPM) in real time via FFT analysis.

## Hardware Concept Analog
Acoustic Sensor -> ADC -> Digital Signal Processing. Mirrors a hardware piezoelectric chest belt streaming analogue voltage to an ADC to derive biometrics.

## Tech Stack
- Sounddevice
- Numpy

## Setup
Ensure you have installed the global packages (`pip install -r requirements.txt`). 
Then, inside the repo root:
```bash
source .venv/bin/activate
cd days/day-05-breathclock
python breathclock.py
```
