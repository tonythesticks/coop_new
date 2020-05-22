'''
Coop

A simple yet complete program to manage and monitor your coop.

Configuration is done in the config.ini file.
Logging is done to the file specified in this config.ini file

'''

import logging
import configparser
from datetime import datetime, timezone, timedelta
import RPi.GPIO as GPIO
import time
from suntime import Sun, SunTimeException
import threading

# config
config = configparser.ConfigParser()
config.read('coop.ini')

# logging
logging.basicConfig(filename=config['Settings']['LogFile'], level=config['Settings']['LogLevel'],
                    format='%(asctime)s - %(levelname)s: %(message)s')

# Suntime
sun = Sun(float(config['Location']['Latitude']), float(config['Location']['Longitude']))
now = (datetime.now(timezone.utc))
offset = int(config['Door']['Offset'])
doortime_open: int = int(config['Door']['Doortime_Open'])
doortime_close: int = int(config['Door']['Doortime_Close'])
opentime = sun.get_sunrise_time()
closetime = sun.get_sunset_time() + timedelta(minutes=(offset))
opentimetomorrow = sun.get_local_sunrise_time(datetime.now() + timedelta(days = 1))
closetimeyesterday = sun.get_local_sunset_time(datetime.now() + timedelta(days = -1)) + timedelta(minutes=(offset))

# GPIO
GPIO.setmode(GPIO.BOARD)
TopSensor = int(config['GPIO']['TopSensor'])
BottomSensor = int(config['GPIO']['BottomSensor'])
GPIO.setup(TopSensor, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BottomSensor, GPIO.IN, pull_up_down=GPIO.PUD_UP)
MotorUp = int(config['GPIO']['IN3'])
GPIO.setup(MotorUp, GPIO.OUT)
MotorDown = int(config['GPIO']['IN4'])
GPIO.setup(MotorDown, GPIO.OUT)
StatusGreen = int(config['GPIO']['StatusGreen'])
GPIO.setup(StatusGreen, GPIO.OUT)
StatusRed = int(config['GPIO']['StatusRed'])
GPIO.setup(StatusRed, GPIO.OUT)
Light = int(config['GPIO']['Light'])
GPIO.setup(Light, GPIO.OUT)
PWM = int(config['GPIO']['ENb'])
GPIO.setup(PMW, GPIO.OUT)
p=GPIO.PWM(PWM,100)
p.start(50)

def status_error():
    GPIO.output(StatusGreen, GPIO.LOW)
    GPIO.output(StatusRed, GPIO.HIGH)

def status_busy():
    while True:
        GPIO.output(StatusRed,GPIO.LOW)
        GPIO.output(StatusGreen,GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(StatusGreen,GPIO.LOW)
        time.sleep(0.5)
        if stop_threads:
            break

def status_ok():
    GPIO.output(StatusGreen, GPIO.HIGH)
    GPIO.output(StatusRed, GPIO.LOW)

def open_door():
    global stop_threads
    stop_threads = False
    print("Open_Door")
    starttime = (datetime.now())
    t1 = threading.Thread(target = status_busy)
    t1.start()
    while True:
        motor_up()
        if GPIO.input(TopSensor) == False:
            motor_stop()
            logging.info("Door is open")
            stop_threads = True
            t1.join()
            motor_stop()
            main_loop()
            break
        elif datetime.now() > starttime + timedelta(milliseconds=(doortime_open)):
            motor_stop()
            logging.error("ERROR, opening door took too long")
            stop_threads = True
            t1.join()
            status_error()
            main_loop()
            break

def close_door():
    global stop_threads
    stop_threads = False
    print("Close_Door")
    starttime = (datetime.now())
    t1 = threading.Thread(target = status_busy)
    t1.start()
    while True:
        motor_down()
        if GPIO.input(BottomSensor) == False:
            motor_stop()
            logging.info("Door is open")
            stop_threads = True
            t1.join()
            motor_stop()
            door()
            break
        elif datetime.now() > starttime + timedelta(microseconds=(doortime_close)):
            motor_stop()
            logging.error("ERROR, closing door took too long")
            stop_threads = True
            t1.join()
            status_error()
            door()
            break

def motor_up():
    p.ChangeDutyCycle(75)
    GPIO.output(MotorUp, GPIO.HIGH)
    GPIO.output(MotorDown, GPIO.LOW)

def motor_down():
    p.ChangeDutyCycle(25)
    GPIO.output(MotorDown, GPIO.HIGH)
    GPIO.output(MotorUp, GPIO.LOW)

def motor_stop():
    GPIO.output(MotorUp, GPIO.LOW)
    GPIO.output(MotorDown, GPIO.LOW)

def startup():
    logging.info('Coop started')
    logging.info("The UTC time is: %s", (now))

def door():
    logging.info("Door will open between %s and %s UTC", opentime,
                 (opentime + timedelta(minutes=2)))
    logging.info("Door will close %s minutes after sunset between %s and %s UTC", offset,
                 closetime, closetime + timedelta(minutes=2))
    count = 0
    if now >= opentime and now <= opentime + timedelta(minutes=2):
        logging.warning("It is day, opening door")
        GPIO.output(Light, GPIO.HIGH)
    #		while GPIO.input(TopSensor) == False and count < doortime:
    #			motor_up()
    #			status_busy()
    #			count = count + 1
    #			logging.debug(count)
    #			logging.debug("Door going up")
    #			if GPIO.input(TopSensor) and GPIO.input(BottomSensor) == False:
    #				motor_stop()
    #				logging.info("Door is open")
    #				status_ok()
    #			if GPIO.input(TopSensor) == False and count == doortime:
    #				motor_stop()
    #				logging.error("ERROR, opening door took too long")
    #				status_error()
    elif now >= closetime and now <= closetime + timedelta(minutes=2):
        logging.warning("It is night, closing door")
        GPIO.output(Light, GPIO.LOW)
    #		while GPIO.input(BottomSensor) == False and count < doortime:
    #			motor_down()
    #			status_busy()
    #			count = count + 1
    #			logging.debug(count)
    #			logging.debug("Door going down")
    #			if GPIO.input(BottomSensor) and GPIO.input(TopSensor) == False:
    #				motor_stop()
    #				logging.info("Door is closed")
    #				status_ok()
    #			if GPIO.input(BottomSensor) == False and count == doortime:
    #				motor_stop()
    #				logging.error("ERROR, closing door took too long")
    #				status_error()
    else:
        if GPIO.input(BottomSensor) and (closetimeyesterday < now > opentime or closetime < now > opentimetomorrow):
            status_ok()
            logging.debug("DoorClosedCheck: OK")
        elif sun.get_sunrise_time() < now < sun.get_sunset_time() and GPIO.input(TopSensor):
            status_ok()
            logging.debug("DoorOpenCheck: OK")
        else:
            status_error()
            logging.error("DoorCheck: ERROR")


def main_loop():
    while True:
        door()
        time.sleep(60)

if __name__ == "__main__":
    try:
#        startup()
        open_door()
#        main_loop()
    except RuntimeError as error:
        print(error.args[0])
    except KeyboardInterrupt:
        print("\nExiting application\n")
        # exit the applications
        GPIO.cleanup()
