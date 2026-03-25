import cv2
import mediapipe as mp
import numpy as np
import subprocess
import time

VOLUME_STEP = 2
TICK_INTERVAL = 0.05
FIST_THRESHOLD = 0.055
HIGH_Y_THRESHOLD = 0.40
LOW_Y_THRESHOLD = 0.60

def get_volume():
    result = subprocess.run(
        ["osascript", "-e", "output volume of (get volume settings)"],
        capture_output=True, text=True
    )
    try:
        return int(result.stdout.strip())
    except:
        return 50

def set_volume(vol):
    vol = max(0, min(100, vol))
    subprocess.run(["osascript", "-e", f"set volume output volume {vol}"])
    return vol

def is_fist(landmarks):
    tips = [8, 12, 16, 20]
    mids = [6, 10, 14, 18]
    curled = 0
    for tip_id, mid_id in zip(tips, mids):
        if landmarks[tip_id].y > landmarks[mid_id].y - FIST_THRESHOLD:
            curled += 1
    return curled >= 3

def fist_position(landmarks):
    return landmarks[0].y

def draw_volume_bar(frame, volume, state):
    h, w = frame.shape[:2]
    bar_x = w - 60
    bar_top = 80
    bar_bot = h - 80
    bar_h = bar_bot - bar_top
    bar_w = 28

    cv2.rectangle(frame, (bar_x, bar_top), (bar_x + bar_w, bar_bot), (50, 50, 50), -1)

    fill_h = int(bar_h * volume / 100)
    fill_top = bar_bot - fill_h
    if state == "up":
        color = (0, 255, 100)
    elif state == "down":
        color = (0, 100, 255)
    else:
        color = (180, 180, 180)
        
    cv2.rectangle(frame, (bar_x, fill_top), (bar_x + bar_w, bar_bot), color, -1)
    cv2.rectangle(frame, (bar_x, bar_top), (bar_x + bar_w, bar_bot), (200, 200, 200), 2)
    cv2.putText(frame, f"{volume}%", (bar_x - 5, bar_bot + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 220, 220), 2)
    cv2.putText(frame, "VOL", (bar_x, bar_top - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

def draw_hud(frame, state, fist_detected):
    h, w = frame.shape[:2]

    if fist_detected:
        if state == "up":
            msg = "FIST UP - VOLUME +"
            color = (0, 255, 100)
        elif state == "down":
            msg = "FIST DOWN - VOLUME -"
            color = (0, 100, 255)
        else:
            msg = "FIST - move up or down"
            color = (200, 200, 200)
    else:
        msg = "No fist detected"
        color = (120, 120, 120)

    cv2.putText(frame, msg, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
    cv2.putText(frame, "Q to quit", (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 120, 120), 1)

def main():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    volume = get_volume()
    last_tick = time.time()
    state = "idle"

    print("VolumeKnuckle running.")
    print("Raise fist -> volume up. Lower fist -> volume down.")
    print("Press Q to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        fist_detected = False
        state = "idle"

        if result.multi_hand_landmarks:
            lms = result.multi_hand_landmarks[0].landmark

            for lm in lms:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 4, (200, 200, 200), -1)

            if is_fist(lms):
                fist_detected = True
                wrist_y = fist_position(lms)

                if wrist_y < HIGH_Y_THRESHOLD:
                    state = "up"
                elif wrist_y > LOW_Y_THRESHOLD:
                    state = "down"
                else:
                    state = "idle"

                xs = [int(lm.x * w) for lm in lms]
                ys = [int(lm.y * h) for lm in lms]
                cx, cy = (min(xs)+max(xs))//2, (min(ys)+max(ys))//2
                radius = max(max(xs)-min(xs), max(ys)-min(ys))//2 + 10
                fist_color = (0,255,100) if state=="up" else (0,100,255) if state=="down" else (180,180,180)
                cv2.circle(frame, (cx, cy), radius, fist_color, 2)

        now = time.time()
        if fist_detected and state != "idle" and (now - last_tick) >= TICK_INTERVAL:
            if state == "up":
                volume = set_volume(volume + VOLUME_STEP)
            elif state == "down":
                volume = set_volume(volume - VOLUME_STEP)
            last_tick = now

        draw_volume_bar(frame, volume, state)
        draw_hud(frame, state, fist_detected)

        cv2.imshow("VolumeKnuckle", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    print("Stopped.")

if __name__ == "__main__":
    main()