from gpiozero import AngularServo
from time import sleep

# GPIO 18 = Physical pin 12
servo = AngularServo(
    18,
    min_angle=0,
    max_angle=180,
    min_pulse_width=0.5 / 1000,
    max_pulse_width=2.5 / 1000
)

print("Moving to 0°")
servo.angle = 0
sleep(3)

print("Moving to 45°")
servo.angle = 45
sleep(3)

print("Moving to 90°")
servo.angle = 90
sleep(3)

print("Moving to 135°")
servo.angle = 135
sleep(3)

print("Moving to 180°")
servo.angle = 180
sleep(3)

servo.detach()
print("Done")
