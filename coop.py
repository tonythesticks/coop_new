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
GPIO.setwarnings(False)
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
Led1 = int(config['GPIO']['Led1'])
GPIO.setup(Led1, GPIO.OUT)
Led2 = int(config['GPIO']['Led2'])
GPIO.setup(Led2, GPIO.OUT)
Led3 = int(config['GPIO']['Led3'])
GPIO.setup(Led3, GPIO.OUT)
PWM = int(config['GPIO']['ENb'])
GPIO.setup(PWM, GPIO.OUT)
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

def Lights(brightness):
    if brightness == 3:
        GPIO.output(Led1, GPIO.HIGH)
        GPIO.output(Led2, GPIO.HIGH)
        GPIO.output(Led3, GPIO.HIGH)
    elif brightness == 2:
        GPIO.output(Led1, GPIO.HIGH)
        GPIO.output(Led2, GPIO.LOW)
        GPIO.output(Led3, GPIO.HIGH)
    elif brightness == 1:
        GPIO.output(Led1, GPIO.LOW)
        GPIO.output(Led2, GPIO.HIGH)
        GPIO.output(Led3, GPIO.LOW)
    elif brightness == 0:
        GPIO.output(Led1, GPIO.LOW)
        GPIO.output(Led2, GPIO.LOW)
        GPIO.output(Led3, GPIO.LOW)

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
    if GPIO.input(TopSensor) == False  and (closetimeyesterday < now < opentime or closetime < now < opentimetomorrow):
        close_door()
        logging.warning("Door was open at startup while it should have been closed")
    elif sun.get_sunrise_time() < now < sun.get_sunset_time() and GPIO.input(BottomSensor) == False:
        open_door()
        logging.debug("Door was closed at startup while it should have been open")
    elif GPIO.input(Bottomsensor) and GPIO.input(TopSensor):
        status_error()
        logging.error('Door is stuck somewhere')
    else:
        logging.info("Door is at right position")

def door():
    logging.debug("Door will open between %s and %s UTC", opentime,
                 (opentime + timedelta(minutes=2)))
    logging.debug("Door will close %s minutes after sunset between %s and %s UTC", offset,
                 closetime, closetime + timedelta(minutes=2))
    if now >= opentime and now <= opentime + timedelta(minutes=2):
        logging.warning("It is day, opening door")
        Lights(3)
        open_door()
    elif now >= closetime and now <= closetime + timedelta(minutes=2):
        logging.warning("It is night, closing door")
        Lights(0)
        close_door()
    else:
        if GPIO.input(BottomSensor) == False and (closetimeyesterday < now < opentime or closetime < now < opentimetomorrow):
            status_ok()
            logging.debug("DoorClosedCheck: OK")
        elif sun.get_sunrise_time() < now < sun.get_sunset_time() and GPIO.input(TopSensor) == False:
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
        startup()
#        main_loop()
    except RuntimeError as error:
        print(error.args[0])
    except KeyboardInterrupt:
        print("\nExiting application\n")
        # exit the applications
        GPIO.cleanup()
