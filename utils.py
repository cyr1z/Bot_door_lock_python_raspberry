import re
import requests
from time import time


def cleanhtml(raw_html):
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext


def open_door():
    response = requests.get("http://192.168.88.167:8081/door").json()
    return response


def open_dog_door():
    response = requests.get("http://192.168.88.167:8081/dog_door").json()
    return response


def old_message(message_data):
    if int(time()) - int(message_data) > 120:
        return True
    return False
