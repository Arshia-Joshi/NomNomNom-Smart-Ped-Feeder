from gpiozero import Servo
from time import sleep

servo = Servo(
    18,
    min_pulse_width=0.5/1000,
    max_pulse_width=2.5/1000
)

while True:
    print("Open")
    servo.max()
    sleep(2)

    print("Close")
    servo.min()
    sleep(2)
