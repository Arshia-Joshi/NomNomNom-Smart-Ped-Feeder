#!/usr/bin/env python3
import os, time
from ultralytics import YOLO
import cv2
from gpiozero import OutputDevice

model = YOLO("yolov8n.pt")
target_classes = {"dog", "cat"}   # class names we care about
FEEDER_PIN = 17
FEED_DURATION = 1.5
COOLDOWN = 10
last_trigger = 0

feeder = OutputDevice(FEEDER_PIN, active_high=True, initial_value=False)

def activate_feeder():
    feeder.on()
    time.sleep(FEED_DURATION)
    feeder.off()

while True:
    # capture frame
    os.system("rpicam-still -o frame.jpg --width 640 --height 480 --quality 80 --timeout 1 -n")

    frame = cv2.imread("frame.jpg")
    results = model.predict(frame, conf=0.35, verbose=False)

    detected = False
    for r in results:
        for cls in r.names.values():
            if cls.lower() in target_classes:
                detected = True
                break

    now = time.time()
    if detected and (now - last_trigger) > COOLDOWN:
        print("DOG/CAT DETECTED → FEEDING")
        activate_feeder()
        last_trigger = now

    # display preview
    cv2.imshow("Live YOLO Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
