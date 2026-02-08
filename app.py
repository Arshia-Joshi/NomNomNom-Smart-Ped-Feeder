import time
import cv2
import numpy as np
from flask import Flask, Response, render_template_string
from ultralytics import YOLO
from collections import deque
from picamera2 import Picamera2
from dog_identity.matcher import identify_dog
from flask import render_template
# ---------------- FLASK ----------------
app = Flask(__name__)

HTML = """
<html>
<head>
    <title>Nom Nom Pet Feeder</title>
</head>
<body>
    <h2>🐶 Live Dog Detection</h2>
    <img src="/video_feed" width="640" height="480">
</body>
</html>
"""

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
DETECTION_COOLDOWN = 1  # seconds
# --------------------------------------

print("Loading YOLO model...")
model = YOLO(MODEL_PATH)
names = model.model.names

last_detection_time = 0
last_dog = "unknown"

# ---------------- CAMERA ----------------
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
    return face

# ---------------- STREAM GENERATOR ----------------
def generate_frames():
    global last_detection_time, last_dog

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

                # -------- IDENTITY LOGIC --------
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

        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes +
            b"\r\n"
        )

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )
@app.route("/dashboard")
def dashboard():
    import psycopg2

    conn = psycopg2.connect(
        dbname="DOG_FEEDER",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )

    with conn.cursor() as cur:
        # Last fed dog
        cur.execute("""
            SELECT d.name, f.exit_time, f.food_dispensed_grams
            FROM feeding_logs f
            JOIN dogs d ON f.dog_id = d.id
            WHERE f.exit_time IS NOT NULL
            ORDER BY f.exit_time DESC
            LIMIT 1
        """)
        last_feed = cur.fetchone()

        # Count feedings today
        cur.execute("""
            SELECT COUNT(*)
            FROM feeding_logs
            WHERE DATE(entry_time) = CURRENT_DATE
        """)
        today_count = cur.fetchone()[0]

        # Full feeding history
        cur.execute("""
            SELECT d.name, f.entry_time, f.exit_time, f.food_dispensed_grams
            FROM feeding_logs f
            JOIN dogs d ON f.dog_id = d.id
            ORDER BY f.entry_time DESC
        """)
        logs = cur.fetchall()

    return render_template(
        "dashboard.html",
        last_feed=last_feed,
        today_count=today_count,
        logs=logs
    )

# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("🌐 Flask server starting on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, threaded=True)
