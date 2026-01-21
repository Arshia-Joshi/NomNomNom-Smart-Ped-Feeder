import os
import time
import cv2
from ultralytics import YOLO
from dog_identity.matcher import identify_dog

# ---------------- CONFIG ----------------
MODEL_PATH = "yolov8n.pt"
IMAGE_PATH = "frame.jpg"
CONFIDENCE = 0.5
DETECTION_COOLDOWN = 15
# ---------------------------------------

print("Loading YOLO model...")
model = YOLO(MODEL_PATH)
names = model.model.names

last_detection_time = 0
last_dog = "unknown"


def crop_dog_face(frame, bbox):
    x1, y1, x2, y2 = bbox
    h = y2 - y1
    if h <= 0:
        return None

    face = frame[y1:y1 + h // 2, x1:x2]
    if face.size == 0:
        return None

    return cv2.cvtColor(face, cv2.COLOR_BGR2RGB)


def generate_frames():
    global last_detection_time, last_dog

    print("📷 rpicam camera started")

    while True:
        # Capture frame using rpicam-still
        os.system(
            f"rpicam-still -o {IMAGE_PATH} "
            f"--width 640 --height 480 --quality 80 -n"
        )

        frame = cv2.imread(IMAGE_PATH)
        if frame is None:
            time.sleep(0.1)
            continue

        results = model.predict(frame, conf=CONFIDENCE, verbose=False)
        res = results[0]

        if res.boxes:
            for box, cls_id, conf in zip(
                res.boxes.xyxy,
                res.boxes.cls,
                res.boxes.conf
            ):
                label = names[int(cls_id)].lower()

                if label == "dog":
                    x1, y1, x2, y2 = map(int, box)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    if time.time() - last_detection_time > DETECTION_COOLDOWN:
                        face = crop_dog_face(frame, (x1, y1, x2, y2))
                        if face is not None:
                            last_dog = identify_dog(face)
                            print("🐶 Identified:", last_dog)
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

        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            frame_bytes +
            b"\r\n"
        )
