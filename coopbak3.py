#! /usr/bin/python3
"""
Coop

A simple yet complete program to manage and monitor your coop.

Configuration is done in the config.ini file.
Logging is done to the file specified in this config.ini file

"""

#TODO: Make 'door' run at every whole minute with something like 'if secondold is > second then do this ... secondold = second'.
#TODO: Make 'door' the main script
#TODO: Implement early-open time
#TODO: Put motor in one definition with variables
#TODO: Put status(led) in one definition with variables

import logging
import configparser
from datetime import datetime, timezone, timedelta
import RPi.GPIO as GPIO
import time
from suntime import Sun
import threading
import urllib.request

# config
config = configparser.ConfigParser()
config.read('/home/pi/projects/coop_new/coop.ini')

# logging
logging.basicConfig(filename=config['Settings']['LogFile'], level=config['Settings']['LogLevel'],
                    format='%(asctime)s - %(levelname)s: %(message)s')

# Suntime
sun = Sun(float(config['Location']['Latitude']), float(config['Location']['Longitude']))
now = (datetime.now(timezone.utc))
offset = int(config['Door']['Offset'])
doortime_open: int = int(config['Door']['Doortime_Open'])
doortime_close: int = int(config['Door']['Doortime_Close'])
opentime = sun.get_sunrise_time() - timedelta(minutes=offset)
closetime = sun.get_sunset_time() + timedelta(minutes=offset)
opentimetomorrow = sun.get_local_sunrise_time(datetime.now() + timedelta(days=1) - timedelta(minutes=offset))
closetimeyesterday = sun.get_local_sunset_time(datetime.now() + timedelta(days=-1)) + timedelta(minutes=offset)
global stop_threads

# GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
TopSensor = int(config['GPIO']['TopSensor'])
BottomSensor = int(config['GPIO']['BottomSensor'])
GPIO.setup(TopSensor, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BottomSensor, GPIO.IN, pull_up_down=GPIO.PUD_UP)
OpenButton = int(config['GPIO']['OpenButton'])
CloseButton = int(config['GPIO']['CloseButton'])
GPIO.setup(OpenButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(CloseButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
MotorUp = int(config['GPIO']['IN3'])
GPIO.setup(MotorUp, GPIO.OUT)
MotorDown = int(config['GPIO']['IN4'])
GPIO.setup(MotorDown, GPIO.OUT)
StatusGreen = int(config['GPIO']['StatusGreen'])
GPIO.setup(StatusGreen, GPIO.OUT)
StatusRed = int(config['GPIO']['StatusRed'])
GPIO.setup(StatusRed, GPIO.OUT)
Led1 = int(config['GPIO']['Led1'])
GPIO.setup(Led1, GPIO.OUT)
Led2 = int(config['GPIO']['Led2'])
GPIO.setup(Led2, GPIO.OUT)
Led3 = int(config['GPIO']['Led3'])
GPIO.setup(Led3, GPIO.OUT)


def status_error():
    GPIO.output(StatusGreen, GPIO.LOW)
    GPIO.output(StatusRed, GPIO.HIGH)


def status_busy():
    while True:
        GPIO.output(StatusRed, GPIO.LOW)
        GPIO.output(StatusGreen, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(StatusGreen, GPIO.LOW)
        time.sleep(0.5)
        if stop_threads:
            break


def status_ok():
    GPIO.output(StatusGreen, GPIO.HIGH)
    GPIO.output(StatusRed, GPIO.LOW)



def open_door():
    #global stop_threads
    #stop_threads = False
    print("Open_Door")
    starttime = (datetime.now())
    #t1 = threading.Thread(target=status_busy)
    #t1.start()
    while True:
        motor_up()
        #if GPIO.input(TopSensor) == False:
        #    time.sleep(1)
        #    motor_stop()
        #    logging.info("Door is open")
        #    stop_threads = True
        #    t1.join()
#       #     main_loop()
        #    break
        if datetime.now() > starttime + timedelta(milliseconds=doortime_open):
            motor_stop()
            #logging.error("ERROR, opening door took too long")
            #stop_threads = True
            #t1.join()
            #status_error()
#            main_loop()
            break


def close_door():
    #global stop_threads
    #stop_threads = False
    print("Close_Door")
    starttime = (datetime.now())
    #ts1 = threading.Thread(target=status_busy)
    #t1.start()
    while True:
        motor_down()
        #if GPIO.input(BottomSensor) == False:
        #    #time.sleep(1) #The sensor is a bit too sensitive (or not well enough placed) so to close entirely it needs another second
        #    motor_stop()
        #    logging.info("Door is closed")
        #    stop_threads = True
        #    t1.join()
#            main_loop()
        #    break
        if datetime.now() > starttime + timedelta(milliseconds=doortime_close):
            motor_stop()
            #logging.error("ERROR, closing door took too long")
            #stop_threads = True
            #t1.join()
            #status_error()
#            main_loop()
            break


def motor_up():
    GPIO.output(MotorUp, GPIO.LOW)
    GPIO.output(MotorDown, GPIO.HIGH)


def motor_down():
    GPIO.output(MotorDown, GPIO.LOW)
    GPIO.output(MotorUp, GPIO.HIGH)


def motor_stop():
    GPIO.output(MotorUp, GPIO.HIGH)
    GPIO.output(MotorDown, GPIO.HIGH)


def startup():
    logging.info('Coop started')
    logging.info("The UTC time is: %s", now)
    if GPIO.input(TopSensor) == False and (closetimeyesterday < now < opentime or closetime < now < opentimetomorrow):
        close_door()
        logging.warning("Door was open at startup while it should have been closed")
        main_loop()
    elif opentime < now < closetime and GPIO.input(BottomSensor) == False:
        open_door()
        logging.debug("Door was closed at startup while it should have been open")
        main_loop()
    elif opentime < now < closetime and GPIO.input(TopSensor) == False:
        logging.info("Door was already open.")
        main_loop()
    elif opentime < now < closetime:
        open_door()
        logging.debug("Doorstatus could not be determined but door should have been and is now open.")
        main_loop()
    elif GPIO.input(BottomSensor) == False  and (closetimeyesterday < now < opentime or closetime < now < opentimetomorrow):
        logging.info("Door was already closed")
        main_loop()
    elif (closetimeyesterday < now < opentime or closetime < now < opentimetomorrow):
        open_door()
        close_door()
        logging.warning("Doorstatus could not be determined but door should have been and is now closed.")
        main_loop()


def door():
    opentime = sun.get_sunrise_time() - timedelta(minutes=offset)
    closetime = sun.get_sunset_time() + timedelta(minutes=offset)
    opentimetomorrow = sun.get_local_sunrise_time(datetime.now() + timedelta(days=1) - timedelta(minutes=offset))
    closetimeyesterday = sun.get_local_sunset_time(datetime.now() + timedelta(days=-1)) + timedelta(minutes=offset)
    now = (datetime.now(timezone.utc))
    next_open = opentime if opentime > now else opentimetomorrow
    next_close = closetime if closetime > now else (sun.get_local_sunset_time(datetime.now() + timedelta(days=1)) + timedelta(minutes=offset))
    #logging.debug("Door will open between %s and %s UTC", next_open,
    #              (next_open + timedelta(minutes=1)))
    #logging.debug("Door will close %s minutes after sunset between %s and %s UTC", offset,
    #              next_close, next_close + timedelta(minutes=1))
    if opentime <= now <= opentime + timedelta(minutes=1):
        logging.warning("Opening door")
        open_door()
        time.sleep(60)
#TODO: Fix this, this should prevent the open_door() to run multiple times which in turn should prevent the motor burning for lack of a topsensor.
        logging.debug("Door will open again at %s UTC", next_open)
        logging.debug("Door will close %s minutes after sunset at %s UTC", offset, next_close)
        main_loop()
    elif closetime <= now <= closetime + timedelta(minutes=1):
        logging.warning("Closing door")
        close_door()
        time.sleep(60)
        logging.debug("Door will open at %s UTC", next_open) 
        logging.debug("Door will close again %s minutes after sunset at %s UTC", offset, next_close)
        main_loop()
    elif GPIO.input(BottomSensor) == False and (closetimeyesterday < now < opentime or closetime < now < opentimetomorrow):
        status_ok()
        logging.debug("DoorClosedCheck: OK")
    elif opentime < now < closetime and GPIO.input(TopSensor) == False:
        status_ok()
        logging.debug("DoorOpenCheck: OK")

    
def main_loop():
    while True:
        for i in range(60):
            if GPIO.input(OpenButton)==0:
                print("Manually Opening")
                logging.debug("Door Manually Opened")
                open_door()
                #time.sleep(0)
            elif GPIO.input(CloseButton)==1:
                print("Manually Closing")
                logging.debug("Door Manually Closed")
                close_door()
                #time.sleep(0)
            else:
                time.sleep(1)       
        door()
        

if __name__ == "__main__":
    try:
        startup()
    except RuntimeError as error:
        print(error.args[0])
    except KeyboardInterrupt:
        print("\nExiting application\n")
        # exit the applications
        GPIO.cleanup()
