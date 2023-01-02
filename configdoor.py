'''
This script is used to determine open/close times of your coop door and record them in milliseconds to fill in the coop.ini file.

If your coop door is anywhere between the bottom and the top, pressing start will bring it right to the top (slowly, so you have time to stop it if necessary).
Pressing C will close the coop door and record the closing time. Pressing O will open the coop door again and record the opening time.

Opening normally is about three times as fast as closing the coop door. If you edit these settings in the coop.py script, you will have to edit them here as well.

Using this script is at your own risk, don't kill chicks.
'''

import logging
import configparser
from datetime import datetime, timezone, timedelta
import RPi.GPIO as GPIO
import time
import threading

# config
config = configparser.ConfigParser()
config.read('coop.ini')

doortime_open: int = 0
doortime_close: int = 0

# GPIO
GPIO.setmode(GPIO.BCM)
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
#PWM = int(config['GPIO']['ENb'])
#GPIO.setup(PWM, GPIO.OUT)
#p = GPIO.PWM(PWM, 100)
#p.start(50)

print("\n")
print("This script is to record the open and close times for the coop door.")
print("Make sure you enter these values in the config.ini file.")
print(" s - Enter = start \n c - Enter = close \n o - Enter = open \n \n You can exit/kill the script with CTRL+C")

def get_doortimes():
    while True:
        x = input()
        if x == 's':
            start()
        elif x == 'c':
            get_closetime()
        elif x == 'o':
            get_opentime()
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
    #p.start(25)
    global stop_threads
    stop_threads = False
    print("Opening_Door for optimal starting position")
    t1 = threading.Thread(target=status_busy)
    t1.start()
    while True:
        motor_up()
        if GPIO.input(TopSensor) == False:
            motor_stop()
            stop_threads = True
            t1.join()
            print("Door is in optimal starting position")
            break


def get_opentime():
    #p.ChangeDutyCycle(25)
    global stop_threads
    stop_threads = False
    print("Open_Door")
    starttime = (datetime.now())
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
    #p.ChangeDutyCycle(75)
    global stop_threads
    stop_threads = False
    print("Close_Door")
    starttime = (datetime.now())
    t1 = threading.Thread(target=status_busy)
    t1.start()
    while True:
        motor_down()
        if GPIO.input(BottomSensor) == False:
            motor_stop()
            doortime_close_raw = datetime.now() - starttime
            doortime_close = round(doortime_close_raw.total_seconds() * 1000)
            print("DoorTime_Close = ", doortime_close)
            stop_threads = True
            t1.join()
            get_doortimes()
            break


def motor_up():
    GPIO.output(MotorUp, GPIO.HIGH)
    GPIO.output(MotorDown, GPIO.LOW)


def motor_down():
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
