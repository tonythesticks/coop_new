import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

Motor1A = 38
Motor1B = 40

GPIO.setup(Motor1A,GPIO.OUT)
GPIO.setup(Motor1B,GPIO.OUT)

print("Going forwards")
GPIO.output(Motor1A,GPIO.HIGH)
GPIO.output(Motor1B,GPIO.LOW)

time.sleep(5)

print("Going backwards")
GPIO.output(Motor1A,GPIO.LOW)
GPIO.output(Motor1B,GPIO.HIGH)

time.sleep(5)

print("Now stop")

GPIO.cleanup()
