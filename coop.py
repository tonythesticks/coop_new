'''
Coop

A simple yet complete porgram to manage and monitor your coop.

Configuration is done in the config.ini file.
Logging is done to the file specified in this config.ini file

'''

import logging
import configparser
from datetime import datetime, timezone
import RPi.GPIO as GPIO
import time
from suntime import Sun, SunTimeException
#import statusled as statusled
#import schedule

#config
config = configparser.ConfigParser()
config.read('config.ini')

#logging
logging.basicConfig(filename=config['Settings']['LogFile'], level=config['Settings']['LogLevel'], format='%(asctime)s - %(levelname)s: %(message)s')

#Suntime
sun = Sun(float(config['Location']['Latitude']), float(config['Location']['Longitude']))
now = datetime.now(timezone.utc)

doortime=10

#GPIO
GPIO.setmode(GPIO.BOARD)
TopSensor= int(config['GPIO']['TopSensor'])
BottomSensor = int(config['GPIO']['BottomSensor'])
GPIO.setup(TopSensor, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BottomSensor, GPIO.IN, pull_up_down=GPIO.PUD_UP)
MotorUp = int(config['GPIO']['MotorUp'])
GPIO.setup(MotorUp,GPIO.OUT)
MotorDown = int(config['GPIO']['MotorDown'])
GPIO.setup(MotorDown,GPIO.OUT)
StatusGreen = int(config['GPIO']['StatusGreen'])
GPIO.setup(StatusGreen,GPIO.OUT)
StatusRed = int(config['GPIO']['StatusRed'])
GPIO.setup(StatusRed,GPIO.OUT)

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

def motor_up():
	GPIO.output(MotorUp,GPIO.HIGH)
	GPIO.output(MotorDown,GPIO.LOW)
	status_busy()

def motor_down():
	GPIO.output(MotorDown,GPIO.HIGH)
	GPIO.output(MotorUp,GPIO.LOW)
	status_busy()

def motor_stop():
	GPIO.output(MotorUp,GPIO.LOW)
	GPIO.output(MotorDown,GPIO.LOW)

def open_door():
	logging.info ("Door going up")
	timestart = time.process_time_ns()
	runtime = 0
#	while GPIO.input(BottomSensor) and GPIO.input(TopSensor) == False:
#		logging.info("Door is closed, opening")
	while GPIO.input(TopSensor) == False and runtime<doortime:
		motor_up()
		runtime=time.process_time_ns()-timestart
		print("runtime: ", runtime)
		print("timestart: ", timestart)
		print("doortime: ", doortime)
		status_busy()
	if GPIO.input(TopSensor) and GPIO.input(BottomSensor) == False:
		logging.info("Door is open")
		status_ok()
		motor_stop()
	if GPIO.input(TopSensor) == False and 10000 > runtime:
		motor_stop()
		logging.error("ERROR, opening door took too long")
		status_error()
#	else:
#		logging.error("Door stuck")
#		status_error()
#		motor_stop()

def close_door():
	logging.info ("Door going down")
	GPIO.output(MotorDown,GPIO.HIGH)
	GPIO.output(MotorUp,GPIO.LOW)
	time.sleep(10)
	GPIO.output(MotorDown,GPIO.LOW)
	if GPIO.input(TopSensor) and GPIO.input(BottomSensor) == False:
		logging.info("Door is open")
	elif GPIO.input(BottomSensor) and GPIO.input(TopSensor) == False:
		logging.info("Door is closed")
	else:
		logging.info("Door in between")


def startup():
	logging.info('Coop started')
	logging.info("The UTC time is: %s", (now))

def door():
	logging.info("Door will open at: %s UTC",(sun.get_sunrise_time()))
	logging.info("Door will close at: %s UTC",(sun.get_sunset_time()))
	if now > sun.get_sunrise_time() and now < sun.get_sunset_time():
		logging.warning("It is day, opening door")
		open_door()
	else:
		logging.warning("It is night, closing door")
		close_door()

def main_loop():
    while True:
        door()
        time.sleep(60)

#while True:
#
#
#	if GPIO.input(TopSensor) and GPIO.input(BottomSensor) == False:
#		logging.info("Door is open")
#	elif GPIO.input(BottomSensor) and GPIO.input(TopSensor) == False:
#		logging.info("Door is closed")
#	else:
#		logging.info("Door in between")

#GPIO.cleanup()

if __name__ == "__main__":
    try:
        startup()
        main_loop()
    except RuntimeError as error:
        print(error.args[0])
    except KeyboardInterrupt:
        print("\nExiting application\n")
        # exit the application
        GPIO.cleanup()
