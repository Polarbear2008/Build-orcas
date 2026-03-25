import cv2
import mediapipe as mp
import numpy as np
import time

EAR_THRESHOLD = 0.20
WINK_DIFF = 0.08
BLINK_TIMEFRAME = 2.5
REQUIRED_BLINKS = 3

L_OUTER, L_INNER, L_TOP, L_BOT = 33, 133, 159, 145
R_OUTER, R_INNER, R_TOP, R_BOT = 263, 362, 386, 374

def calc_ear(landmarks, p_top, p_bot, p_out, p_in, w, h):
    top = np.array([landmarks[p_top].x * w, landmarks[p_top].y * h])
    bot = np.array([landmarks[p_bot].x * w, landmarks[p_bot].y * h])
    out_pt = np.array([landmarks[p_out].x * w, landmarks[p_out].y * h])
    in_pt = np.array([landmarks[p_in].x * w, landmarks[p_in].y * h])
    
    v_dist = np.linalg.norm(top - bot)
    h_dist = np.linalg.norm(out_pt - in_pt)
    
    if h_dist == 0: return 0.0
    return v_dist / h_dist

def main():
    mp_face = mp.solutions.face_mesh
    face_mesh = mp_face.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    cv2.namedWindow('BlinkLock', cv2.WINDOW_NORMAL)
    locked = False
    
    both_closed_last_frame = False
    blink_times = []
    
    print("BlinkLock running.")
    print("Blink 3 times fast to lock. Wink to unlock. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = face_mesh.process(rgb)
        
        ear_l = 0.0
        ear_r = 0.0
        
        if results.multi_face_landmarks:
            lms = results.multi_face_landmarks[0].landmark
            
            ear_l = calc_ear(lms, L_TOP, L_BOT, L_OUTER, L_INNER, w, h)
            ear_r = calc_ear(lms, R_TOP, R_BOT, R_OUTER, R_INNER, w, h)
            
            left_closed = ear_l < EAR_THRESHOLD
            right_closed = ear_r < EAR_THRESHOLD
            both_closed = left_closed and right_closed
            
            if both_closed_last_frame and not both_closed and not locked:
                blink_times.append(time.time())
                print("Blink detected.")
                
            both_closed_last_frame = both_closed
            
            current_time = time.time()
            blink_times = [t for t in blink_times if current_time - t <= BLINK_TIMEFRAME]
            
            if not locked:
                if len(blink_times) >= REQUIRED_BLINKS:
                    print("Locking screen.")
                    locked = True
                    blink_times.clear()
                    cv2.setWindowProperty('BlinkLock', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                wink_left = left_closed and not right_closed and (ear_r - ear_l) > WINK_DIFF
                wink_right = right_closed and not left_closed and (ear_l - ear_r) > WINK_DIFF
                
                if wink_left or wink_right:
                    print("Unlocked via wink.")
                    locked = False
                    blink_times.clear()
                    cv2.setWindowProperty('BlinkLock', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            
            if not locked:
                cv2.putText(frame, f"L EAR: {ear_l:.2f}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
                cv2.putText(frame, f"R EAR: {ear_r:.2f}", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
                cv2.putText(frame, f"Blinks: {len(blink_times)} / {REQUIRED_BLINKS}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                
                if left_closed: cv2.putText(frame, "LEFT CLOSED", (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                if right_closed: cv2.putText(frame, "RIGHT CLOSED", (250, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        if locked:
            display = np.zeros((h, w, 3), dtype=np.uint8)
            text1 = "LOCKED"
            text2 = "- WINK TO UNLOCK -"
            font = cv2.FONT_HERSHEY_SIMPLEX
            (tw1, th1), _ = cv2.getTextSize(text1, font, 2.5, 5)
            (tw2, th2), _ = cv2.getTextSize(text2, font, 1.0, 2)
            cv2.putText(display, text1, ((w - tw1) // 2, (h // 2) - 30), font, 2.5, (0, 0, 255), 5)
            cv2.putText(display, text2, ((w - tw2) // 2, (h // 2) + 50), font, 1.0, (200, 200, 200), 2)
        else:
            display = frame
            
        cv2.imshow('BlinkLock', display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if 'hands' in locals(): hands.close() 
    face_mesh.close()
    cap.release()
    cv2.destroyAllWindows()
    print("Stopped.")

if __name__ == "__main__":
    main()
