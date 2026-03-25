import cv2
import mediapipe as mp
import pygame
import sys
import os

MUSIC_FILE = "rock.wav"
LOOK_DOWN_THRESHOLD = 15

def is_looking_away(landmarks):
    nose = landmarks[1]
    left_eye = landmarks[33]
    right_eye = landmarks[263]
    mouth = landmarks[14]

    eye_mid_y = (left_eye.y + right_eye.y) / 2
    
    face_width = max(right_eye.x - left_eye.x, 0.001)
    yaw_ratio = (nose.x - left_eye.x) / face_width

    face_height = max(mouth.y - eye_mid_y, 0.001)
    pitch_ratio = (nose.y - eye_mid_y) / face_height

    looking_left_right = yaw_ratio < 0.35 or yaw_ratio > 0.65
    looking_up_down = pitch_ratio < 0.35 or pitch_ratio > 0.65

    return (looking_left_right or looking_up_down), yaw_ratio, pitch_ratio

def main():
    if not os.path.exists(MUSIC_FILE):
        print(f"Error: Music file '{MUSIC_FILE}' not found.")
        sys.exit(1)

    pygame.mixer.init()
    pygame.mixer.music.load(MUSIC_FILE)

    mp_face = mp.solutions.face_mesh
    face_mesh = mp_face.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        sys.exit(1)

    print("RockLook is running.")
    print("Look away to play music, look at screen to pause.")
    print("Press 'q' in the video window to quit.")

    is_playing = False

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Lost webcam feed.")
                break

            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                looking_away, yr, pr = is_looking_away(landmarks)

                if looking_away and not is_playing:
                    pygame.mixer.music.play(-1)
                    is_playing = True
                    print("Looking away - playing music")

                elif not looking_away and is_playing:
                    pygame.mixer.music.pause()
                    is_playing = False
                    print("Looking at screen - paused")
                    
                cv2.putText(frame, f"Yaw: {yr:.2f} (Limits: 0.35 - 0.65)", (20, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, f"Pitch: {pr:.2f} (Limits: 0.35 - 0.65)", (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            cv2.imshow('RockLook', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        cap.release()
        cv2.destroyAllWindows()
        face_mesh.close()

if __name__ == "__main__":
    main()