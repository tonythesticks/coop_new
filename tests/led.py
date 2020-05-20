import RPi.GPIO as GPIO
import time

RED = 10
GREEN = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(GREEN,GPIO.OUT)
GPIO.setup(RED,GPIO.OUT)
while(True):
	print("Green LED for 10 seconds")
	GPIO.output(GREEN,GPIO.HIGH)
	GPIO.output(RED,GPIO.LOW)
	time.sleep(10)
	print( "Red LED for 10 seconds")
	GPIO.output(GREEN,GPIO.LOW)
	GPIO.output(RED,GPIO.HIGH)
	time.sleep(10)

Message = input("Press enter to stop")
GPIO.cleanup()
