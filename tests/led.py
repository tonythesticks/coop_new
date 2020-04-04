import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(12,GPIO.OUT)
GPIO.setup(10,GPIO.OUT)
print "Door open"
GPIO.output(12,GPIO.HIGH)
GPIO.output(10,GPIO.LOW)
time.sleep(10)
print "Door closed"
GPIO.output(12,GPIO.LOW)
GPIO.output(10,GPIO.HIGH)
