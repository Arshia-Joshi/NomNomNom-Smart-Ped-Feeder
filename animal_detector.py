#!/usr/bin/env python3
"""
animal_detector.py
Detect ONLY dog, cat, bird using YOLOv8 (snapshot mode).
Terminal-based detection output.
"""

import os
import time
import cv2
from ultralytics import YOLO

# ================= CONFIG =================
MODEL_PATH = "yolov8n.pt"
IMAGE_PATH = "frame.jpg"
ALLOWED_CLASSES = {"dog", "cat", "bird"}
CONFIDENCE = 0.35
STABLE_FRAMES = 3
CAPTURE_DELAY = 0.4
# ==========================================

print("Loading YOLO model...")
model = YOLO(MODEL_PATH)
names = model.model.names

stable_count = 0
print("Starting animal detection (CTRL+C to stop)...\n")

try:
    while True:
        # 1️⃣ Capture snapshot from Pi camera
        os.system(
            f"rpicam-still -o {IMAGE_PATH} "
            f"--width 640 --height 480 --quality 80 -n"
        )

        frame = cv2.imread(IMAGE_PATH)
        if frame is None:
            print("❌ Camera frame not read")
            time.sleep(0.5)
            continue

        # 2️⃣ Run YOLO
        results = model.predict(
            frame,
            conf=CONFIDENCE,
            imgsz=640,
            verbose=False
        )

        res = results[0]
        detected = []

        # 3️⃣ Filter ONLY dog, cat, bird
        if res.boxes:
            for cls_id, conf in zip(res.boxes.cls, res.boxes.conf):
                label = names[int(cls_id)].lower()
                confidence = float(conf)

                if label in ALLOWED_CLASSES:
                    detected.append(f"{label} ({confidence:.2f})")

        # 4️⃣ Print detection to TERMINAL
        if detected:
            stable_count += 1
            print(f"DETECTED → {', '.join(detected)}  [{stable_count}/{STABLE_FRAMES}]")
        else:
            stable_count = 0
            print("DETECTED → nothing")

        # 5️⃣ Confirm detection after stable frames
        if stable_count >= STABLE_FRAMES:
            print(f"\n✅ CONFIRMED ANIMAL: {detected}\n")
            stable_count = 0

        time.sleep(CAPTURE_DELAY)

except KeyboardInterrupt:
    print("\nStopped by user (camera released)")
    os.system("pkill -f rpicam-still")
