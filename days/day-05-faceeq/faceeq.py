import cv2
import mediapipe as mp
import numpy as np
import scipy.io.wavfile as wavfile
from scipy.signal import resample
import sounddevice as sd
import sys

AUDIO_FILE = "rock.wav"
BLOCKSIZE = 1024

play_idx = 0.0
play_dir = 1.0
play_speed = 1.0
audio_data = None
total_samples = 0

def audio_callback(outdata, frames, time_info, status):
    global play_idx

    if status or audio_data is None:
        outdata.fill(0)
        return

    req_frames = int(frames * play_speed * abs(play_dir))
    
    if req_frames == 0 or play_dir == 0:
        outdata.fill(0)
        return
        
    start_i = int(play_idx)
    end_i = start_i + req_frames
    
    if end_i >= total_samples:
        end_i = total_samples - 1
        req_frames = end_i - start_i
        if req_frames <= 0:
            outdata.fill(0)
            return
            
    if start_i < 0:
        start_i = 0
        req_frames = end_i - start_i
        if req_frames <= 0:
            outdata.fill(0)
            return

    chunk = audio_data[start_i:end_i]
    if play_dir < 0:
        chunk = chunk[::-1]
        
    if len(chunk) > 0:
        try:
            resampled = resample(chunk, frames)
            if resampled.ndim == 1:
                resampled = np.expand_dims(resampled, axis=1)
                
            if resampled.shape[1] == 1 and outdata.shape[1] == 2:
                resampled = np.repeat(resampled, 2, axis=1)
            elif resampled.shape[1] == 2 and outdata.shape[1] == 1:
                resampled = np.mean(resampled, axis=1, keepdims=True)
                
            outdata[:] = resampled
        except Exception:
            outdata.fill(0)
    else:
        outdata.fill(0)
        
    if play_dir > 0:
        play_idx += req_frames
    else:
        play_idx -= req_frames
        if play_idx < 0:
            play_idx = 0

def main():
    global audio_data, total_samples, play_dir, play_speed
    
    try:
        sample_rate, data = wavfile.read(AUDIO_FILE)
        if data.dtype == np.int16:
            audio_data = data.astype(np.float32) / 32768.0
        else:
            audio_data = data.astype(np.float32)
            
        total_samples = len(audio_data)
        channels = 2 if audio_data.ndim == 2 else 1
    except Exception as e:
        print(f"Error loading {AUDIO_FILE}: {e}")
        sys.exit(1)

    mp_face = mp.solutions.face_mesh
    face_mesh = mp_face.FaceMesh(max_num_faces=1, refine_landmarks=False)
    cap = cv2.VideoCapture(0)
    
    print("FaceEQ core running.")
    stream = sd.OutputStream(
        samplerate=sample_rate, 
        channels=channels, 
        blocksize=BLOCKSIZE, 
        callback=audio_callback
    )
    
    with stream:
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)
            
            if results.multi_face_landmarks:
                lms = results.multi_face_landmarks[0].landmark
                nose = lms[1]
                left_cheek = lms[234]
                right_cheek = lms[454]
                left_eye = lms[159]
                right_eye = lms[386]
                
                cheek_width = right_cheek.x - left_cheek.x
                if cheek_width > 0:
                    nose_pos = (nose.x - left_cheek.x) / cheek_width
                    if nose_pos > 0.65:
                        play_dir = -2.0
                    elif nose_pos < 0.35:
                        play_dir = 2.0
                    else:
                        play_dir = 1.0
                
                eye_diff = right_eye.y - left_eye.y
                if eye_diff > 0.05:
                    play_speed = 1.6
                elif eye_diff < -0.05:
                    play_speed = 0.6
                else:
                    play_speed = 1.0
            else:
                play_dir = 0
                
            cv2.imshow("FaceEQ", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    cap.release()
    cv2.destroyAllWindows()
    print("Stopped.")

if __name__ == "__main__":
    main()
