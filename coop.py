import logging
import configparser
import datetime
import RPi.GPIO as GPIO
import time
import pytz
from suntime import Sun, SunTimeException

utc=pytz.UTC

#config
config = configparser.ConfigParser()
config.read('config.ini')

#logging
logging.basicConfig(filename=config['Settings']['LogFile'], level=config['Settings']['LogLevel'], format='%(asctime)s - %(levelname)s: %(message)s')

#Suntime
latitude = float(config['Location']['Latitude'])
longitude = float(config['Location']['Longitude'])
sun = Sun(latitude, longitude)

#GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(int(config['GPIO']['TopSensor']), GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(int(config['GPIO']['BottomSensor']), GPIO.IN, pull_up_down=GPIO.PUD_UP)
TopSensor= int(config['GPIO']['TopSensor'])
BottomSensor = int(config['GPIO']['BottomSensor'])

#This is where the magic happens
logging.info('Coop started')

print(datetime.datetime.utcnow())
print(sun.get_sunrise_time())

if datetime.datetime.utcnow() > sun.get_local_sunrise_time().replace(tzinfo=utc):
	print(day)
else:
	print(night)
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
