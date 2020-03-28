import re
import RPi.GPIO as GPIO
from time import sleep, time

Relay_Ch2 = 20
Relay_Ch3 = 21
# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(Relay_Ch2, GPIO.OUT)
# GPIO.setup(Relay_Ch3, GPIO.OUT)


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def open_door():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Relay_Ch2, GPIO.OUT)
    GPIO.output(Relay_Ch2, GPIO.LOW)
    sleep(0.5)
    GPIO.output(Relay_Ch2, GPIO.HIGH)

def open_dog_door():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Relay_Ch3, GPIO.OUT)
    GPIO.output(Relay_Ch3, GPIO.LOW)
    sleep(0.5)
    GPIO.output(Relay_Ch3, GPIO.HIGH)

def pin_clean():
    GPIO.cleanup()

def old_message(message_data):
    if int(time()) - int(message_data) > 120:
        return True
    return False
