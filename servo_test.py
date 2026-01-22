from gpiozero import Servo
from time import sleep

print("Starting servo test...")

servo = Servo(
    18,                      # GPIO 18 (BCM) → Physical pin 12
    min_pulse_width=0.5/1000,
    max_pulse_width=2.5/1000
)

print("Move to CENTER")
servo.mid()
sleep(3)

print("Move to OPEN (max)")
servo.max()
sleep(3)

print("Move to CLOSE (min)")
servo.min()
sleep(3)

servo.detach()
print("Test finished")
