import RPi.GPIO as GPIO
import time

SERVO_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

def open_servo():
    pwm.ChangeDutyCycle(7.5)  # adjust angle if needed
    time.sleep(0.5)

def close_servo():
    pwm.ChangeDutyCycle(2.5)
    time.sleep(0.5)
