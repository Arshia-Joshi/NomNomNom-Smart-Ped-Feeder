from ultralytics import YOLO
import cv2
import time
from dog_identity.matcher import identify_dog

# -----------------------------
# Load YOLOv8 model
# -----------------------------
model = YOLO("yolov8n.pt")

# -----------------------------
# Open rpicam using OpenCV (V4L2)
# -----------------------------
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

if not cap.isOpened():
    print("❌ Camera could not be opened")
    exit()

# Set resolution (important for Raspberry Pi)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("📷 rpicam camera started")

# -----------------------------
# Dog identification control
# -----------------------------
last_identified_dog = None
last_detection_time = 0
DETECTION_COOLDOWN = 15  # seconds

# -----------------------------
# Face crop helper
# -----------------------------
def crop_dog_face(frame, bbox):
    """
    Crop upper half of dog bounding box (face region)
    frame: BGR image
    bbox: (x1, y1, x2, y2)
    """
    x1, y1, x2, y2 = bbox

    h, w, _ = frame.shape
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    box_height = y2 - y1
    if box_height <= 0:
        return None

    # Upper half of bounding box = face
    face = frame[y1 : y1 + box_height // 2, x1 : x2]

    if face.size == 0:
        return None

    # Convert BGR → RGB (VERY IMPORTANT)
    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    return face

# -----------------------------
# Main loop
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to read frame")
        break

    # Run YOLO detection
    results = model(frame, verbose=False)

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            conf = float(box.conf[0])

            if label == "dog" and conf > 0.5:
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                current_time = time.time()

                # Cooldown check
                if current_time - last_detection_time >= DETECTION_COOLDOWN:
                    face = crop_dog_face(frame, (x1, y1, x2, y2))

                    if face is not None:
                        dog_name = identify_dog(face)

                        print("🐶 Identified dog:", dog_name)

                        last_identified_dog = dog_name
                        last_detection_time = current_time

                        # Show name on screen
                        cv2.putText(
                            frame,
                            dog_name,
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 0, 255),
                            2
                        )

                        # -----------------------------
                        # FEEDER LOGIC (placeholder)
                        # -----------------------------
                        if dog_name == "karu":
                            print("🍖 Dispense food for Karu")
                        elif dog_name == "snow":
                            print("🍖 Dispense food for Snow")
                        else:
                            print("🍖 Dispense food for Unknown dog")

    # Show live feed
    cv2.imshow("NomNom Dog Feeder (rpicam)", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
print("🛑 Program stopped")
