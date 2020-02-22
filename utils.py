import re
import RPi.GPIO as GPIO
from time import sleep

Relay_Ch2 = 20
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(Relay_Ch2, GPIO.OUT)


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def open_door():
    GPIO.output(Relay_Ch2, GPIO.LOW)
    sleep(0.5)
    GPIO.output(Relay_Ch2, GPIO.HIGH)
