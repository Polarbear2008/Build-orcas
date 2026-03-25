# BUILDCORED ORCAS

**30 Days. 30 Projects. Zero Hardware Required.**

A daily build challenge that teaches hardware engineering thinking through software projects you can run on any laptop.

| | |
|---|---|
| **Projects** | 30 |
| **Weeks** | 4 |
| **Time per day** | ~1 hour |
| **Cloud dependencies** | 0 |

Works on Mac, Windows, and Linux. All AI runs locally — no API keys, no cloud, no cost.

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/buildcored-orcas.git
cd buildcored-orcas
python verify_setup.py
```

Follow the [Environment Setup Guide](SETUP_GUIDE.md) to install all dependencies before Day 1.

## Projects Directory

Here are the completed daily projects so far:
- **Day 1**: [RockLook](days/day-01-rocklook) - Webcam gaze detection triggering rock music playback.
- **Day 2**: [AirCanvas](days/day-02-aircanvas) - Draw on an invisible canvas using finger pinches.
- **Day 3**: [VolumeKnuckle](days/day-03-volumeknuckle) - Raise and lower your fist to control Mac system volume.
- **Day 4**: [BlinkLock](days/day-04-blinklock) - Lock your screen with rapid blinks, unlock with a wink.
- **Day 5**: [FaceEQ](days/day-05-faceeq) - Turn your head to scrub a song, tilt to change the pitch.
- **Day 6**: [BreathClock](days/day-06-breathclock) - Listen to your breathing and calculate BPM using microphone inputs.
- **Day 7**: [KeyboardOscilloscope](days/day-07-keyboardoscilloscope) - Press keys to synthesize tones and form visible chords.
- **Day 8**: [PocketAgent](days/day-08-pocketagent) - Run an AI assistant entirely on your laptop. No internet required.
- **Day 9**: [WhisperDesk](days/day-09-whisperdesk) - Talk to your laptop and it types what you say offline.
- **Day 10**: [TerminalBrain](days/day-10-terminalbrain) - Terminal wrapper that actively watches for shell errors and suggests AI fixes offline.
- **Day 11**: [MoodSynth](days/day-11-moodsynth) - Type a semantic mood, and the AI synthesizes an infinite ambient soundscape to match.
- **Day 12**: [SnapAnnotator](days/day-12-snapannotator) - Accesses the webcam and uses edge VLM inference to label everything it sees.

## What Is This?

BUILDCORED ORCAS is a 30-day daily build challenge for people with Python fundamentals who want to develop hardware engineering intuition — without owning any hardware.

Every day, you build a complete, working project in about an hour. Each project targets a real hardware concept — PWM, I2C, ADC, cache architecture, interrupt handlers, PID control — implemented entirely in software on your laptop.

**The core mental model:** sensor → process → output. Your webcam is a sensor. Your microphone is an ADC. Your screen is an actuator.

## The 4 Weeks

| Week | Theme | Focus |
|------|-------|-------|
| 1 | Body as Input | Webcam + mic as sensors. Gesture, gaze, breath → digital actions |
| 2 | Local AI Core | On-device LLMs via ollama. Edge inference, memory budgets, latency |
| 3 | Signals & Systems | FFT, filters, PWM, I2C, DAQ — hardware fundamentals in software |
| 4 | Full Systems | Sensor → model → actuator pipelines. System integration |

## What You Need

- A laptop (Mac, Windows, or Linux) with a webcam and microphone
- Python 3.10+
- About 1 hour per day for 30 consecutive days
- Willingness to ship imperfect code daily

## Submission Format

Every project must include a completed README using the [template](templates/README_TEMPLATE.md). This is part of the "shipped" definition.

## What Comes Next: ORCAS v2.0

After 30 days of software-first thinking, v2.0 puts real chips in your hands. Raspberry Pi Pico W, real sensors, real actuators. The PID controller from Day 23 drives a real servo. The I2C protocol from Day 19 reads a real accelerometer. The PWM from Day 17 dims a real LED.

v1.5 is the foundation. v2.0 is where it becomes physical.

## Community

BUILDCORED ORCAS runs as a cohort challenge on Discord and Telegram. You'll have a squad of 5 people, a squad lead for daily support, and mentors for technical guidance.

## Repository Structure

```
buildcored-orcas/
├── verify_setup.py          # Run this first — checks your environment
├── SETUP_GUIDE.md           # Full setup instructions
├── assets/
│   ├── semaphore_landmarks.csv   # Baseline dataset for Day 27 (SignalFlags)
│   ├── firmware_blob.bin         # Simulated firmware for Day 25 (FirmwarePatcher)
│   └── datasheets/               # Component datasheets for Day 24 (HardwareTA)
├── templates/
│   └── README_TEMPLATE.md        # Required README format for every project
└── days/                         # Day-specific resources (populated during challenge)
```
