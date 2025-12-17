#!/usr/bin/env python3
"""
animal_detector_visual.py
Visual test: shows bounding boxes for dog, cat, bird
"""

import os
import time
import cv2
from ultralytics import YOLO

# -------- CONFIG --------
MODEL_PATH = "yolov8n.pt"
IMAGE_PATH = "frame.jpg"
ALLOWED_CLASSES = {"dog", "cat", "bird"}
CONFIDENCE = 0.30
CAPTURE_DELAY = 0.5
# ------------------------

print("Loading YOLO model...")
model = YOLO(MODEL_PATH)
names = model.model.names

print("Starting VISUAL animal detection")
print("Show an image of a dog/cat/bird to the camera")
print("Press Q to quit\n")

while True:
    # 1️⃣ Capture frame
    os.system(
        f"rpicam-still -o {IMAGE_PATH} "
        f"--width 640 --height 480 --quality 80 -n"
    )

    frame = cv2.imread(IMAGE_PATH)
    if frame is None:
        print("Failed to read frame")
        continue

    # 2️⃣ YOLO prediction
    results = model.predict(
        frame,
        conf=CONFIDENCE,
        imgsz=640,
        verbose=False
    )

    res = results[0]

    # 3️⃣ Draw bounding boxes ONLY for allowed animals
    if res.boxes:
        for box, cls_id, conf in zip(
            res.boxes.xyxy,
            res.boxes.cls,
            res.boxes.conf
        ):
            label = names[int(cls_id)].lower()

            if label in ALLOWED_CLASSES:
                x1, y1, x2, y2 = map(int, box)
                text = f"{label} {conf:.2f}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    frame, text, (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 0), 2
                )

    # 4️⃣ Show image window
    cv2.imshow("Animal Detection Test", frame)

    # 5️⃣ Exit on Q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(CAPTURE_DELAY)

cv2.destroyAllWindows()
print("Stopped.")
