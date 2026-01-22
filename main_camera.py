import os
import time
import cv2
import numpy as np
from ultralytics import YOLO
from collections import deque
from dog_identity.matcher import identify_dog

# ---------------- IDENTITY SMOOTHING ----------------
SCORE_WINDOW = 5
THRESHOLD = 0.63
MARGIN = 0.04

score_buffer = {
    "karu": deque(maxlen=SCORE_WINDOW),
    "snow": deque(maxlen=SCORE_WINDOW),
}

# ---------------- CONFIG ----------------
MODEL_PATH = "yolov8n.pt"
IMAGE_PATH = "frame.jpg"
CONFIDENCE = 0.5
DETECTION_COOLDOWN = 15  # seconds
# ---------------------------------------

print("Loading YOLO model...")
model = YOLO(MODEL_PATH)
names = model.model.names

last_detection_time = 0
last_dog = "unknown"


# ---------------- FACE CROP ----------------
def crop_dog_face(frame, bbox):
    x1, y1, x2, y2 = bbox
    h = y2 - y1
    if h <= 0:
        return None

    face = frame[y1:y1 + h // 2, x1:x2]
    if face.size == 0:
        return None

    return cv2.cvtColor(face, cv2.COLOR_BGR2RGB)


# ---------------- MAIN STREAM ----------------
def generate_frames():
    global last_detection_time, last_dog

    print("📷 rpicam camera started")

    while True:
        # Capture frame
        os.system(
            f"rpicam-still -o {IMAGE_PATH} "
            f"--width 640 --height 480 "
            f"--brightness 0.65 "
            f"--contrast 1.2 "
            f"--exposure normal "
            f"--gain 1.0 "
            f"--shutter 8000 "
            f"--quality 80 -n "
            f"> /dev/null 2>&1"
        )

        frame = cv2.imread(IMAGE_PATH)
        if frame is None:
            time.sleep(0.1)
            continue

        results = model.predict(frame, conf=CONFIDENCE, verbose=False)
        res = results[0]

        if res.boxes:
            for box, cls_id in zip(res.boxes.xyxy, res.boxes.cls):
                label = names[int(cls_id)].lower()

                if label != "dog":
                    continue

                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # ---------- IDENTITY LOGIC ----------
                if time.time() - last_detection_time > DETECTION_COOLDOWN:
                    face = crop_dog_face(frame, (x1, y1, x2, y2))

                    if face is not None:
                        name, score = identify_dog(face)

                        if name in score_buffer:
                            score_buffer[name].append(score)

                            avg_score = np.mean(score_buffer[name])

                            # Second-best score
                            other_scores = [
                                np.mean(buf)
                                for other_name, buf in score_buffer.items()
                                if other_name != name and buf
                            ]

                            second_best = max(other_scores) if other_scores else 0

                            if avg_score > THRESHOLD and (avg_score - second_best) > MARGIN:
                                last_dog = name
                            else:
                                last_dog = "unknown"

                            print(
                                f"🐶 {name} | avg={avg_score:.3f} "
                                f"| second={second_best:.3f} → {last_dog}"
                            )

                            last_detection_time = time.time()

                cv2.putText(
                    frame,
                    last_dog,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

        # Stream to Flask
        _, buffer = cv2.imencode(".jpg", frame)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes()
            + b"\r\n"
        )
