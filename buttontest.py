import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(9,GPIO.OUT)
GPIO.setup(10,GPIO.OUT)
GPIO.setup(2,GPIO.IN)
GPIO.setup(3,GPIO.IN)

while 1:
    if GPIO.input(2)==0:
        GPIO.output(9,0)
        print("UP")
    else:
        GPIO.output(9,1)
        #print("Stop")
        
    if GPIO.input(3)==1:
        GPIO.output(10,0)
        print("DOWN")
    else:
        GPIO.output(10,1)
        #print("Stop")
