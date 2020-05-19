import configparser
import RPi.GPIO as GPIO
import time

# config
config = configparser.ConfigParser()
config.read('coop.ini')

# GPIO
GPIO.setmode(GPIO.BOARD)
StatusGreen = int(config['GPIO']['StatusGreen'])
GPIO.setup(StatusGreen, GPIO.OUT)
StatusRed = int(config['GPIO']['StatusRed'])
GPIO.setup(StatusRed, GPIO.OUT)

def status_error():
    GPIO.output(StatusGreen, GPIO.LOW)
    GPIO.output(StatusRed, GPIO.HIGH)

def status_busy():
    GPIO.output(StatusRed, GPIO.LOW)
    GPIO.output(StatusGreen, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(StatusGreen, GPIO.LOW)
    time.sleep(0.5)

def status_ok():
    GPIO.output(StatusGreen, GPIO.HIGH)
    GPIO.output(StatusRed, GPIO.LOW)