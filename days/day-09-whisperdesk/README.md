# WhisperDesk

Speak to your laptop and watch it type your words universally across any application. Entirely offline, utilizing rolling environmental noise baselines.

## Hardware Concept Analog
Acoustic Sensor + Noise Gate -> Edge NPU Pipeline -> Physical Actuator. Acts identically to an offline hardware microphone array feeding an embedded LLM that mechanically actuates a USB keyboard.

## Tech Stack
- Faster-Whisper (Int8 Quantized inference)
- Sounddevice (Acoustic dynamic VAD)
- Pynput (Keyboard actuation)
- Rich (UX Dashboard)

## Setup
Ensure you have installed the global packages (`pip install -r requirements.txt`).
```bash
source ../../.venv/bin/activate
cd days/day-09-whisperdesk
python whisperdesk.py
```
> **Note:** The first time you speak into the microphone, MacOS will prompt you to grant **Accessibility Permissions** to your Terminal application. You MUST grant this permission so `pynput` can emulate the physical keystrokes across your operating system.
