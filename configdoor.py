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

doortime_open: int = 0
doortime_close: int = 0

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
PWM = int(config['GPIO']['ENb'])
GPIO.setup(PWM, GPIO.OUT)
p = GPIO.PWM(PWM, 100)
p.start(50)

print("\n")
print("This script is to record the open and close times for the coop door.")
print("Make sure you enter these values in the config.ini file.")
print("s-start c-close o-open k-kill e-exit")
print("\n")

def get_doortimes():
    while True:
    x = raw_input()
        if x == 's':
            print("Door going up for start position")
            start()
        elif x == 'c':
            get_closetime()
        elif x == 'o':
            get_opentime()
        elif x == 'k':
            motor_stop()
        elif raw_input() == 'e':
            GPIO.cleanup()
            print("GPIO Clean up")
            break
        else:
            print("<<<  wrong data  >>>")
            print("please enter the defined data to continue.....")

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

def start():
    global stop_threads
    stop_threads = False
    print("Opening_Door")
    t1 = threading.Thread(target=status_busy)
    t1.start()
    while True:
        motor_up()
        if GPIO.input(TopSensor) == False:
            motor_stop()
            stop_threads = True
            t1.join()
            break

def get_opentime():
    global stop_threads
    stop_threads = False
    print("Open_Door")
    starttime = (datetime.now())
    print(starttime)
    t1 = threading.Thread(target=status_busy)
    t1.start()
    while True:
        motor_up()
        if GPIO.input(TopSensor) == False:
            motor_stop()
            doortime_open_raw = datetime.now() - starttime
            doortime_open = round(doortime_open_raw.total_seconds() * 1000)
            print("DoorTime_Open = ", doortime_open)
            stop_threads = True
            t1.join()
            get_doortimes()
            break


def get_closetime():
    global stop_threads
    stop_threads = False
    print("Close_Door")
    starttime = (datetime.now())
    print(starttime)
    t1 = threading.Thread(target=status_busy)
    t1.start()
    while True:
        motor_down()
        if GPIO.input(BottomSensor) == False:
            motor_stop()
            doortime_close_raw = datetime.now() - starttime
            doortime_close = round(doortime_close_raw.total_seconds() * 1000)
            print("DoorTime_Close = ", doortime_open)
            stop_threads = True
            t1.join()
            get_doortimes()
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


if __name__ == "__main__":
    try:
        get_doortimes()
    except RuntimeError as error:
        print(error.args[0])
    except KeyboardInterrupt:
        print("\nExiting application\n")
        # exit the applications
        GPIO.cleanup()
