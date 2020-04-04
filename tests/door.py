
import RPi.GPIO as GPIO #import the GPIO library
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)

TopSensor = 8
BottomSensor =7

#name = "Ryan"
#print("Hello " + name)

while True:
    if GPIO.input(TopSensor) and GPIO.input(BottomSensor) == False:
       print("Door is open")
       time.sleep(1)
    elif GPIO.input(BottomSensor) and GPIO.input(TopSensor) == False:
       print("Door is closed")
       time.sleep(1)
    else:
       print("Door in between")
       time.sleep(1)

GPIO.cleanup()
