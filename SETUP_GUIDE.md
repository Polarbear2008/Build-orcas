# 🐋 BUILDCORED ORCAS — Pre-Launch Checklist

**Complete everything below before Day 1 — March 25, 8:00 AM**
Deadline for setup verification: Monday March 24, midnight.

---

## ⚙️ Step 1: Software Setup

Everything you need installed takes ~30 minutes

### Install Python 3.10+

Open the Terminal on your PC. 

**macOS:**

```
brew install python@3.12
```

**Windows:**
Download from [python.org](https://python.org/). **Check “Add Python to PATH” during install.**

**Linux:**

```
sudo apt-get install python3.12 python3.12-venv python3-pip
```

**Verify:**

```
python3 --version
```

- [ ]  Python 3.10+ installed and verified

---

### Install system dependencies + Python packages

**macOS:**

```
brew install portaudio
pip install opencv-python mediapipe numpy scipy matplotlib pygame sounddevice pyaudio librosa psutil rich gitpython Pillow pyttsx3 pynput faster-whisper chromadb sentence-transformers PyMuPDF textual scikit-learn
```

**Windows:**

```
pip install opencv-python mediapipe numpy scipy matplotlib pygame sounddevice pyaudio librosa psutil rich gitpython Pillow pyttsx3 pynput faster-whisper chromadb sentence-transformers PyMuPDF textual scikit-learn
```

If pyaudio fails: `pip install pipwin && pipwin install pyaudio`

**Linux:**

```
sudo apt-get install portaudio19-dev python3-pyaudio python3-tk
pip install opencv-python mediapipe numpy scipy matplotlib pygame sounddevice pyaudio librosa psutil rich gitpython Pillow pyttsx3 pynput faster-whisper chromadb sentence-transformers PyMuPDF textual scikit-learn
```

- [ ]  All Python packages installed

---

### Install ollama + pull AI models

**Install ollama:**
- macOS: `brew install ollama` or download from [ollama.com](https://ollama.com/)
- Windows/Linux: Download from [ollama.com](https://ollama.com/)

**Start the server** (keep this terminal open):

```
ollama serve
```

**In a NEW terminal, pull the models** (~2-4 GB download):

```
ollama pull qwen2.5:3b
ollama pull moondream
```

**Verify:**

```
ollama list
```

- [ ]  ollama installed and running
- [ ]  Both models pulled (qwen2.5:3b and moondream)

---

### Install Git + configure

```
git --version
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

- [ ]  Git installed and configured

---

### Clone the repo + run verification

```
git clone https://github.com/PeterVanPercson/buildcored-orcas.git
cd buildcored-orcas
python verify_setup.py
```

The script checks everything — Python, packages, webcam, mic, ollama, git. Every check must show **PASS**.

If something fails, the script tells you the exact fix command for your OS. Run it, then re-run the script.

- [ ]  All checks PASS
- [ ]  Screenshot taken of passing results

---

## 🤝 Step 2: Join the Community

### ⭐ Star the GitHub repo

Go to [github.com/PeterVanPercson/buildcored-orcas](https://github.com/PeterVanPercson/buildcored-orcas) and click the ⭐ **Star** button in the top right.

- [ ]  Repo starred

---

### Join the Discord server

**This is where the entire challenge happens.** Telegram is for reminders only.

👉 [**Join Discord**](https://discord.gg/WqPwnX9n)

After joining:
1. Read **#rules-and-info** completely — this is your orientation
2. Introduce yourself in **#introductions** (name, location, why you joined)
3. Post your `verify_setup.py` screenshot in **#tech-support**

- [ ]  Joined Discord
- [ ]  Introduced myself
- [ ]  Posted setup screenshot

---

## 💡 Step 3: Recommended (not must, but helps)

These aren’t required to start Day 1, but will save you time later.

- [ ]  **Install OBS Studio** — Free screen recorder from [obsproject.com](https://obsproject.com/). Required on Advanced/Expert days (Day 10+). Mac users can use Cmd+Shift+5 instead. Windows users can use Win+G.
- [ ]  **Install VS Code** — Download from [code.visualstudio.com](https://code.visualstudio.com/). Any editor works, but VS Code’s integrated terminal makes the workflow faster.
- [ ]  **Test your webcam** — Open Photo Booth (Mac) or Camera app (Win). Confirm you see yourself. If using external USB webcam, plug it in now.
- [ ]  **Test your microphone** — Open system audio settings. Speak. Confirm the input level moves.

---

## 🚨 If you’re stuck

Post in **#tech-support** on Discord with this exact format:

```
OS: [Mac/Windows/Linux] | Check: [which step] | Error: [exact message] | Tried: [what you did]
```

Your squad lead responds within 1 hour. If unresolved, they escalate to the mentor.

**Do not wait until Monday night.** Fix issues now.
