import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(2,GPIO.IN)
GPIO.setup(3,GPIO.IN)

while True:
    for i in range(10):
        if GPIO.input(2)==0:
            print("Manually Opening")
            #logging.debug("Door Manually Opened")
            #Open_Door()
            time.sleep(3)
        if GPIO.input(3)==1:
            print("Manually Closing")
            #logging.debug("Door Manually Closed")
            #Close_Door()
            time.sleep(3)
        time.sleep(1)       
    print("Door" + time.strftime("%H:%M:%S", time.localtime()))#door()
    #time.sleep(60)
