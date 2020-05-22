import RPi.GPIO as GPIO #import the GPIO library
#import time

##GPIO settings
TopSensor = 11
BottomSensor = 12
GreenLed = 16
RedLed = 18
GPIO.setmode(GPIO.BOARD)
GPIO.setup(TopSensor, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BottomSensor, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GreenLed,GPIO.OUT)
GPIO.setup(RedLed,GPIO.OUT)


##Define events and their actions
def door_open(channel):
	print("Door Opened")
	GPIO.output(GreenLed,GPIO.HIGH)
	GPIO.output(RedLed,GPIO.LOW)
def door_closed(channel):
	print("Door closed")
	GPIO.output(GreenLed,GPIO.LOW)
	GPIO.output(RedLed,GPIO.HIGH)

##Detect events
GPIO.add_event_detect(TopSensor,GPIO.FALLING,callback=door_open,bouncetime=2000)
GPIO.add_event_detect(BottomSensor,GPIO.FALLING,callback=door_closed,bouncetime=2000)

##Check door status every second
#while True:
#    if GPIO.input(TopSensor) and GPIO.input(BottomSensor) == False:
#       print("Door is open")
#       time.sleep(1)
#    elif GPIO.input(BottomSensor) and GPIO.input(TopSensor) == False:
#       print("Door is closed")
#       time.sleep(1)
#    else:
#       print("Door in between")
#       time.sleep(1)

Message = input("Press enter to quit\n\n")

GPIO.cleanup()
