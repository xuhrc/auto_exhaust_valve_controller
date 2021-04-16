#!/usr/bin/env python
import socket
import datetime
import time
import sys
import os
import time
import valve

MODE = '01'
ELM_PROMPT = '>'
root_dir = os.getcwd()
strings = []

print '\nTool_SW_Vers: '
version = os.path.basename(__file__)
print version
print 'developed by xuhrc'


# ------FUNCTIONS--------------------------------------------------------------------


def send_cmd(cmd):
    data = ''
    cmd += "\r"  # terminate
    s.send(cmd)
    i = 0
    while True:
        data = data + s.recv(64)
        i = i + 1
        if data.endswith(ELM_PROMPT) or len(data) > 128 or i > 10:
            if len(data) > 128:
                s.send("\r")
            break
    # remove the prompt character
    data = data[:-1]
    # splits into lines while removing empty lines and trailing spaces
    data = data.replace('\r', '')
    data = data[len(cmd) - 1:]
    """time.sleep(1)"""
    return data


def get_dec(PID):
    response = send_cmd(MODE + PID)
    resp = str(response).split(" ")
    if resp[0] != '41' or str(PID) != resp[1]:
        raise ValueError('get dec failed')
    print(str(resp))
    A = resp[2]
    B = resp[3]
    if B == '':
        B = '00'
    return [int(A, 16), int(B, 16)]


"""INIT DONGLE-------------------------------------"""

global s


def reconnect():
    global s
    s = socket.socket()
    s.settimeout(2.0)
    host = '192.168.0.10'  # needs to be in quote
    port = 35000
    s.connect((host, port))
    print('connected obd')
    send_cmd("\r")
    send_cmd("ATSP0")
    send_cmd("ATD")
    protocol = send_cmd("ATDPN")[1:]
    send_cmd("0100")
    send_cmd("ATAT2")


speed35 = False


def sync():
    global speed35
    speed = get_dec('0D')[0]
    rpm_dec = get_dec('0C')
    rpm = (256 * rpm_dec[0] + rpm_dec[1]) / 4

    if rpm >= 2500 or speed >= 65:
        speed35 = speed > 35
        logRpmAndSpeed(rpm_dec, rpm, speed)
        valve.open_valve()
        return

    if (speed <= 35 and speed35) or rpm <= 1200:
        speed35 = False
        logRpmAndSpeed(rpm_dec, rpm, speed)
        valve.close_valve()
        return

    if speed > 35:
        speed35 = True


def logRpmAndSpeed(rpm_dec, rpm, speed):
    print('rpm dec' + str(rpm_dec))
    print('rpm:' + str(rpm) + ' rpm')
    print('speed:' + str(speed) + ' speed')


fail_times = 0


def monitor():
    global fail_times
    try:
        sync()
        fail_times = 0
    except socket.error:
        fail_times = fail_times + 1
        print "\r\nsocket error,do reconnect "
        try:
            reconnect()
        except:
            print("reconnect failed")
    except Exception as e:
        fail_times = fail_times + 0.01
        print('sync failed')
        print(e)

    if fail_times >= 10:
        valve.open_valve()
