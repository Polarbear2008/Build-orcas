import numpy as np
import sounddevice as sd
import time
import sys

SAMPLE_RATE = 16000
CHUNK_SIZE = 2048
FREQ_LOW = 200
FREQ_HIGH = 2500

class BreathTracker:
    def __init__(self):
        self.energy_history = [0.0] * 50
        self.history_len = 50
        self.recent_breaths = []
        self.last_breath_time = 0
        self.state = "IDLE"
        self.cooldown = 1.2
        self.active_breath_start = 0

    def process_chunk(self, indata):
        window = np.hanning(len(indata))
        data = indata.flatten() * window
        
        fft_data = np.abs(np.fft.rfft(data))
        freqs = np.fft.rfftfreq(len(data), 1.0 / SAMPLE_RATE)
        
        breath_mask = (freqs > FREQ_LOW) & (freqs < FREQ_HIGH)
        total_energy = np.sum(fft_data)
        
        if total_energy == 0:
            return 0.0, 0.1, 0, False

        breath_energy = np.sum(fft_data[breath_mask])
        breath_ratio = breath_energy / total_energy
        
        self.energy_history.append(breath_energy)
        if len(self.energy_history) > self.history_len:
            self.energy_history.pop(0)

        is_windy = breath_ratio > 0.35
        
        baseline = np.mean(self.energy_history)
        std_dev = np.std(self.energy_history)
        threshold = max(baseline + (std_dev * 1.5), 0.2)

        now = time.time()
        registered = False
        
        if is_windy and breath_energy > threshold:
            if self.state == "IDLE" and (now - self.last_breath_time) > self.cooldown:
                self.state = "INHALING"
                self.active_breath_start = now
        elif breath_energy < baseline * 1.2:
            if self.state == "INHALING":
                if now - self.active_breath_start > 0.2:
                    self.state = "IDLE"
                    self.last_breath_time = now
                    self.recent_breaths.append(now)
                    registered = True
                else:
                    self.state = "IDLE"
                
        self.recent_breaths = [b for b in self.recent_breaths if now - b <= 60.0]
        bpm = len(self.recent_breaths)
        
        return breath_energy, threshold, bpm, registered

tracker = BreathTracker()

def get_sparkline(val, max_val):
    chars = "  ▂▃▄▅▆▇█"
    idx = int((val / max_val) * (len(chars) - 1))
    return chars[max(0, min(idx, len(chars)-1))]

def callback(indata, frames, time_info, status):
    if status:
        return
        
    energy, threshold, bpm, registered = tracker.process_chunk(indata)
    spark = get_sparkline(energy, max(threshold * 2.0, 0.1))
    
    if registered:
        print(f"\nBreath detected. BPM: {bpm}")
    else:
        print(f"BPM: {bpm:02d} | Signal [{spark}] Raw: {energy:5.1f} / Thresh: {threshold:5.1f}   ", end='\r')

def main():
    print("BreathClock running.")
    print("Listening to microphone to calculate BPM...")
    print("Press Ctrl+C to quit.\n")
    
    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, blocksize=CHUNK_SIZE, callback=callback):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
