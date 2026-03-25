# SnapAnnotator

A native edge application that captures optical data from your webcam and pushes it through a completely offline Vision-Language Model (`moondream`) to annotate the environment in real-time.

## Hardware Concept Analog
Optical Scanner Array -> Local Frame Buffer -> Embedded Perception NPU. Acts identically to the visual array logic inside an autonomous drone or smart-camera.

## Tech Stack
- OpenCV (`cv2`): Frame extraction & hardware exposure calibration
- Ollama Moondream: Offline Visual Context Inference
- Base64 + Urllib: Payload serialization
- Rich: TUI Markdown Streaming

## Setup
Ensure your local Ollama daemon is active and you have pulled the `moondream` model as defined in your Pre-Launch checklist.

```bash
source ../../.venv/bin/activate
cd days/day-12-snapannotator
python snapannotator.py
```

> **Note:** MacOS may prompt you to grant Camera/Webcam permissions to Terminal the first time the sensor warms up!
