##################################################

#           P26 ----> Relay_Ch1
#			P20 ----> Relay_Ch2
#			P21 ----> Relay_Ch3

##################################################
# !/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import time

Relay_Ch1 = 26


# Relay_Ch2 = 20
# Relay_Ch3 = 21

def init():
    setup()
    GPIO.output(Relay_Ch1, GPIO.HIGH)
    print("--------------disable valve--------------")


def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(Relay_Ch1, GPIO.OUT)
    # GPIO.setup(Relay_Ch2, GPIO.OUT)
    # GPIO.setup(Relay_Ch3, GPIO.OUT)
    print("Setup The Relay Module is [success]")


status = False

open_counter = 0


def open_valve():
    global status
    if status:
        return

    # Control the Channel 1
    global open_counter
    open_counter += 1
    setup()
    GPIO.output(Relay_Ch1, GPIO.LOW)
    time.sleep(1)

    status = True

    print("+++++++++++++open valve++++++++++++++, counter=%d" % open_counter)


close_counter = 0


def close_valve():
    global status
    if not status:
        return

    global close_counter
    close_counter += 1
    # Control the Channel 1
    setup()
    GPIO.output(Relay_Ch1, GPIO.HIGH)
    time.sleep(1)

    status = False
    print("--------------close valve--------------, counter=%d" % close_counter)
