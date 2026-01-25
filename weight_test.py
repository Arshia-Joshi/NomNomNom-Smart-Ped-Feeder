import time
import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

DT = 5
SCK = 6
hx = HX711(DT, SCK)

# 🔒 FINAL CALIBRATION VALUES
OFFSET = -179842.536
SCALE  = 226.6910952380952

def read_average(samples=15):
    readings = []
    for _ in range(samples):
        val = hx.get_raw_data()
        if isinstance(val, list):
            readings.extend(val)
        elif val is not None:
            readings.append(val)
        time.sleep(0.01)
    return sum(readings) / len(readings)

print("HX711 running...\n")

try:
    while True:
        raw = read_average()
        weight = (raw - OFFSET) / SCALE

        # 🧹 noise cleanup
        if abs(weight) < 5:
            weight = 0

        print(f"Weight: {weight:.1f} g")
        time.sleep(0.25)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nExit cleanly")
