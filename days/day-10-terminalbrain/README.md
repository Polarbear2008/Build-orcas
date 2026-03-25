# TerminalBrain

A native bash wrapper that intercepts shell exceptions entirely offline using edge LLM inference, diagnosing stack traces instantly using your local NPU/CPU.

## Hardware Concept Analog
Hardware exception handling logic. This replaces standard core dump files with live neural interrupt handlers.

## Tech Stack
- Subprocess Pipe Interception
- Ollama API (`urllib`)
- Rich (Dashboarding)

## Setup
Ensure the local Ollama daemon is running (`ollama serve`). 
Wrap any command you want to execute around `terminalbrain.py`:
```bash
source ../../.venv/bin/activate
cd days/day-10-terminalbrain
python terminalbrain.py "ls /this/folder/does/not/exist"
```
Or use it to natively debug falling scripts:
```bash
python terminalbrain.py "python bad_script.py"
```
