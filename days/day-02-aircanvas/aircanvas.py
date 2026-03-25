import cv2
import mediapipe as mp
import numpy as np

PINCH_THRESHOLD = 80
BRUSH_THICKNESS = 4
COLORS = [
    (0, 255, 255),
    (0, 0, 255),
    (0, 255, 0),
    (255, 0, 255),
    (255, 165, 0),
]

def dist(a, b):
    return np.hypot(a[0] - b[0], a[1] - b[1])

def landmark_px(lm, w, h):
    return int(lm.x * w), int(lm.y * h)

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

    canvas = None
    strokes = []
    current_stroke = []
    prev_point = None
    was_pinching = False
    color_idx = 0

    print("AirCanvas running.")
    print("Pinch index and thumb to draw. Release to lift.")
    print("Keys: c=color, z=undo, x=clear, q=quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        if canvas is None:
            canvas = np.zeros((h, w, 3), dtype=np.uint8)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        pinching = False
        index_tip = None

        if results.multi_hand_landmarks:
            lms = results.multi_hand_landmarks[0].landmark
            index_tip = landmark_px(lms[8], w, h)
            thumb_tip = landmark_px(lms[4], w, h)

            d = dist(index_tip, thumb_tip)
            pinching = d < PINCH_THRESHOLD

            for id in [4, 8]:
                pt = landmark_px(lms[id], w, h)
                cv2.circle(frame, pt, 8, COLORS[color_idx], -1)

            color_line = (0, 255, 0) if pinching else (100, 100, 100)
            cv2.line(frame, index_tip, thumb_tip, color_line, 2)

        if pinching and index_tip:
            if prev_point:
                cv2.line(canvas, prev_point, index_tip, COLORS[color_idx], BRUSH_THICKNESS)
                current_stroke.append((prev_point, index_tip, COLORS[color_idx]))
            prev_point = index_tip
        else:
            if was_pinching and current_stroke:
                strokes.append(current_stroke)
                current_stroke = []
            prev_point = None

        was_pinching = pinching

        display = cv2.addWeighted(frame, 0.5, canvas, 1.0, 0)

        color_swatch = COLORS[color_idx]
        cv2.circle(display, (30, 30), 14, color_swatch, -1)
        cv2.putText(display, "C:color  Z:undo  X:clear  Q:quit",
                    (55, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
        if pinching:
            cv2.putText(display, "DRAWING", (w - 120, 36),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS[color_idx], 2)

        cv2.imshow("AirCanvas", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            color_idx = (color_idx + 1) % len(COLORS)
            print("Color changed")
        elif key == ord('z'):
            if strokes:
                strokes.pop()
                canvas = np.zeros((h, w, 3), dtype=np.uint8)
                for stroke in strokes:
                    for (p1, p2, col) in stroke:
                        cv2.line(canvas, p1, p2, col, BRUSH_THICKNESS)
                print("Stroke undone")
            else:
                print("Nothing to undo")
        elif key == ord('x'):
            canvas = np.zeros((h, w, 3), dtype=np.uint8)
            strokes.clear()
            current_stroke.clear()
            print("Canvas cleared")

    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    print("Stopped.")

if __name__ == "__main__":
    main()