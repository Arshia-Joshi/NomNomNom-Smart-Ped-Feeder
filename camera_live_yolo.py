import time
import cv2
import numpy as np
from ultralytics import YOLO
from collections import deque
from picamera2 import Picamera2
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
CONFIDENCE = 0.5
DETECTION_COOLDOWN = 15  # seconds
# ---------------------------------------

print("Loading YOLO model...")
model = YOLO(MODEL_PATH)
names = model.model.names

last_detection_time = 0
last_dog = "unknown"

# ---------------- CAMERA SETUP ----------------
picam2 = Picamera2()
picam2.configure(
    picam2.create_video_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    )
)
picam2.start()
time.sleep(1)

print("📷 Picamera2 live stream started")

# ---------------- FACE CROP ----------------
def crop_dog_face(frame, bbox):
    x1, y1, x2, y2 = bbox
    h = y2 - y1
    if h <= 0:
        return None

    face = frame[y1:y1 + h // 2, x1:x2]
    if face.size == 0:
        return None

    return face  # already RGB

# ---------------- MAIN LOOP ----------------
while True:
    frame = picam2.capture_array()

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

    cv2.imshow("Nom Nom Feeder – Live", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ---------------- CLEANUP ----------------
cv2.destroyAllWindows()
picam2.stop()
