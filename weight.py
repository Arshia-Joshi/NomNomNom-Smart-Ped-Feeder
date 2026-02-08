import time
import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

hx = HX711(5, 6)

print("Remove all weight (taring)...")
time.sleep(2)

tare = sum(hx.get_raw_data()) / len(hx.get_raw_data())
print("Tare value:", tare)
print("Place weight on sensor\n")

try:
    while True:
        raw = hx.get_raw_data()

        if raw:
            avg_raw = sum(raw) / len(raw)
            net_value = abs(avg_raw - tare)

            # Noise filter
            if net_value < 500:
                net_value = 0

            print("Weight (raw units):", round(net_value, 2))
        else:
            print("No data")

        time.sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup()
