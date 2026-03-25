# MoodSynth

A fully offline, entirely procedural infinite ambient soundscape generator. Type a semantic mood (e.g. "dark rainy cyberpunk city"), and the edge LLM translates that sentiment into raw mathematical DSP parameters to synthesize custom audio indefinitely.

## Hardware Concept Analog
CV Output Mapping. Replaces physical modular synth patch-cables (LFO, VCA, Mixers) with purely autonomous parametric adjustments dictated by an intelligent semantic classifier.

## Tech Stack
- Ollama Local NPU (Semantic to Vector Parametric Mapping)
- Numpy + SoundDevice (Additive Noise Synthesis & Amplitude Control)
- Rich (Hardware Dashboard)

## Setup
Ensure the local Ollama daemon is running (`ollama serve`).

```bash
source ../../.venv/bin/activate
cd days/day-11-moodsynth
python moodsynth.py
```
> **Warning**: Ensure your audio volume is set to ~50% before running to prevent startling loud swells depending on your generated LFO matrices.
