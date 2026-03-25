import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wavfile
from faster_whisper import WhisperModel
from pynput.keyboard import Controller
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
import time
import os

SAMPLE_RATE = 16000
SILENCE_TIMEOUT = 1.0

keyboard = Controller()
console = Console()

def type_text(text):
    text = text.strip()
    if not text: return
    # Emulate mechanical keystrokes
    keyboard.type(f"{text} ")

def main():
    console.print("[bold yellow]Loading Neural Edge (Faster-Whisper base.en int8)...[/bold yellow]")
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    console.print("[bold green]WhisperDesk Core Intialized.[/bold green]\n")
    
    bg_noise = 0.01
    audio_buffer = []
    is_recording = False
    silence_start = 0

    def callback(indata, frames, time_info, status):
        nonlocal bg_noise, is_recording, silence_start, audio_buffer
        if status: return
        
        rms = np.sqrt(np.mean(indata**2))
        
        # Dynamic environmental noise tracking (rolling average)
        if not is_recording:
            bg_noise = (bg_noise * 0.95) + (rms * 0.05)
            
        threshold = max(bg_noise * 3.0, 0.02) 
        
        if rms > threshold:
            if not is_recording:
                is_recording = True
            audio_buffer.append(indata.copy())
            silence_start = 0
        elif is_recording:
            audio_buffer.append(indata.copy())
            if silence_start == 0:
                silence_start = time.time()
            elif time.time() - silence_start > SILENCE_TIMEOUT:
                is_recording = False

    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback)
    
    try:
        with stream:
            with Live(refresh_per_second=10) as live:
                while True:
                    time.sleep(0.1)
                    
                    state_color = "red" if is_recording else "cyan"
                    status_text = "VOCAL TRACT DETECTED [RECORDING]" if is_recording else "MONITORING ENVIRONMENT"
                    
                    # Hardware simulation UI
                    panel = Panel(
                        f"Status: [{state_color}]{status_text}[/{state_color}]\n\n"
                        f"Ambient RMS Baseline : {bg_noise:.4f} dB\n"
                        f"Acoustic Gate Trigger: {max(bg_noise * 3.0, 0.02):.4f} dB\n"
                        f"Ring Buffer Size     : {len(audio_buffer)} chunks",
                        title="WhisperDesk Dynamic VAD"
                    )
                    live.update(panel)
                    
                    if not is_recording and len(audio_buffer) > 0:
                        live.update(Panel("[yellow]Analyzing neural weights...[/yellow]", title="WhisperDesk DSP"))
                        audio_data = np.concatenate(audio_buffer)
                        audio_buffer = []
                        
                        tmp_file = "temp_dictation.wav"
                        wavfile.write(tmp_file, SAMPLE_RATE, audio_data)
                        
                        segments, info = model.transcribe(tmp_file, beam_size=5)
                        text = " ".join([seg.text for seg in segments])
                        
                        if os.path.exists(tmp_file):
                            os.remove(tmp_file)
                            
                        if text.strip():
                            type_text(text)
                            
    except KeyboardInterrupt:
        pass
        
    console.print("\n[bold red]Terminated.[/bold red]")

if __name__ == "__main__":
    main()
