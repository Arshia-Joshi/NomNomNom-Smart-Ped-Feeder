from gpiozero import Servo
from time import sleep, time

# ================= CONFIG =================
SERVO_PIN = 18          # GPIO 18 (PWM)
OPEN_TIME = 1.2         # seconds servo stays open
COOLDOWN = 30           # seconds between feeds

# Servo pulse widths (calibrate if needed)
MIN_PW = 0.5 / 1000     # closed
MAX_PW = 2.5 / 1000     # open

# ==========================================

servo = Servo(
    SERVO_PIN,
    min_pulse_width=MIN_PW,
    max_pulse_width=MAX_PW
)

last_feed_time = 0


def dispense_food():
    global last_feed_time

    now = time()
    if now - last_feed_time < COOLDOWN:
        print("⏳ Cooldown active — skipping feed")
        return

    print("🍖 Dispensing food...")
    servo.max()          # open
    sleep(OPEN_TIME)
    servo.min()          # close
    sleep(0.3)

    servo.detach()       # 🔥 stop jitter
    last_feed_time = now

    print("✅ Feeding complete")


# ================= TEST LOOP =================
if __name__ == "__main__":
    print("NomNomNom Servo Controller Ready 🐶")

    try:
        while True:
            cmd = input("Press ENTER to feed (q to quit): ")
            if cmd.lower() == "q":
                break

            dispense_food()

    except KeyboardInterrupt:
        pass

    finally:
        servo.detach()
        print("\n🛑 Servo safely stopped")
