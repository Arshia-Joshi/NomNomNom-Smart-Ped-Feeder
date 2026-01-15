import pigpio
import time

SERVO_PIN = 18  # GPIO18 (Pin 12)

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("❌ pigpio daemon not running")

def open_feeder():
    """
    Rotate servo to OPEN position
    """
    pi.set_servo_pulsewidth(SERVO_PIN, 1500)  # ~90 degrees
    print("🔓 Feeder OPEN")

def close_feeder():
    """
    Rotate servo to CLOSED position
    """
    pi.set_servo_pulsewidth(SERVO_PIN, 500)   # ~0 degrees
    print("🔒 Feeder CLOSED")

def cleanup():
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop()
