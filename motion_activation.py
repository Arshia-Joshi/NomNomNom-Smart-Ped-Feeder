import cv2
import time

# -----------------------------
# Camera Setup
# -----------------------------
cap = cv2.VideoCapture(0)

# Reduce resolution (important for Pi)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# -----------------------------
# Motion Detector
# -----------------------------
motion_detector = cv2.createBackgroundSubtractorMOG2(
    history=200,
    varThreshold=50,
    detectShadows=True
)

# -----------------------------
# Motion Detection Function
# -----------------------------
def detect_motion(frame):
    fg_mask = motion_detector.apply(frame)

    # Remove shadows (gray pixels)
    _, thresh = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

    motion_pixels = cv2.countNonZero(thresh)

    return motion_pixels > 1500  # 🔧 TUNE THIS IF NEEDED


# -----------------------------
# Main Loop
# -----------------------------
activated = False
last_motion_time = 0
RESET_DELAY = 2  # seconds

print("📷 Camera started. Waiting for motion...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Camera error")
        break

    motion = detect_motion(frame)

    if motion:
        last_motion_time = time.time()

        if not activated:
            activated = True
            print("🚨 MOTION DETECTED → SYSTEM ACTIVATED")

    else:
        # Reset only after delay (prevents flicker)
        if activated and (time.time() - last_motion_time > RESET_DELAY):
            activated = False
            print("✅ No motion → SYSTEM IDLE")

    # Optional display (disable on headless Pi)
    cv2.imshow("Nom Nom Motion Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -----------------------------
# Cleanup
# -----------------------------
cap.release()
cv2.destroyAllWindows()
print("🛑 Camera stopped")
