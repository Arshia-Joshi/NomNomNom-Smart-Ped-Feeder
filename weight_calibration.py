import time
import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

DT = 5
SCK = 6
hx = HX711(DT, SCK)

def read_average(samples=30):
    readings = []
    for _ in range(samples):
        val = hx.get_raw_data()
        if isinstance(val, list):
            readings.extend(val)
        elif val is not None:
            readings.append(val)
        time.sleep(0.01)
    return sum(readings) / len(readings)

# -------- TARE --------
print("\nSTEP 1: Remove EVERYTHING from scale")
time.sleep(3)

OFFSET = read_average(50)
print("OFFSET =", OFFSET)

# -------- CALIBRATION --------
KNOWN_WEIGHT = 168.0  # Samsung S24
print(f"\nSTEP 2: Place Samsung S24 ({KNOWN_WEIGHT} g) on scale")
time.sleep(5)

RAW_WITH_PHONE = read_average(50)
print("RAW WITH PHONE =", RAW_WITH_PHONE)

SCALE = (RAW_WITH_PHONE - OFFSET) / KNOWN_WEIGHT
print("\nSCALE =", SCALE)

GPIO.cleanup()

print("\n✅ Calibration complete")
print("👉 Save OFFSET and SCALE values")
