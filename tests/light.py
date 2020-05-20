import RPi.GPIO as GPIO
import time

LED = 15

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(LED,GPIO.OUT)
while(True):
	print("Led on")
	GPIO.output(LED,GPIO.HIGH)
	time.sleep(10)
	print( "Led off")
	GPIO.output(LED,GPIO.LOW)
	time.sleep(10)

Message = input("Press enter to stop")
GPIO.cleanup()
