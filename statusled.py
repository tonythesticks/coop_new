def status_error():
	GPIO.output(StatusGreen,GPIO.LOW)
	GPIO.output(StatusRed,GPIO.HIGH)

def status_busy():
	GPIO.output(StatusRed,GPIO.LOW)
	GPIO.output(StatusGreen,GPIO.HIGH)
	time.sleep(0.5)
	GPIO.output(StatusGreen,GPIO.LOW)
	time.sleep(0.5)

def status_ok():
	GPIO.output(StatusGreen,GPIO.HIGH)
	GPIO.output(StatusRed,GPIO.LOW)
