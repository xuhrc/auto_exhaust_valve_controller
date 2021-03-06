# this receiver is used for artsure OBDII device
# The OBD device will broadcast instant speed and rpm data every 200-300ms via UDP
import socket
from threading import Thread
import time
import subprocess


import valve


class ObdReceiver(Thread):

    def __init__(self):
        super(ObdReceiver, self).__init__()
        self.rpm = 0
        self.speed = 0
        self.lastReceiveTime = time.time()

    def run(self):
        while True:
            try:
                self.listening()
            except Exception as e:
                print(e)

    def listening(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # Enable broadcasting mode
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        client.bind(('', 50000))
        counter = 0
        try:
            while True:
                data, addr = client.recvfrom(1024)
                self.lastReceiveTime = time.time()

                if data.startswith("ATZ"):
                    data_str_arr = data.replace("ATZ", "").split(",")
                    rpm_str = data_str_arr[0].replace("R", "")
                    speed_str = data_str_arr[1].replace("S", "")

                    self.rpm = int(rpm_str, 10)
                    self.speed = int(speed_str, 10)

                # log speed and rpm data every 10 times
                if counter > 10:
                    print("%s, received message: %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), data))
                    counter = 0
                counter += 1
        finally:
            client.close()


speed35 = False


def sync(obd_receiver):
    global speed35
    rpm = obd_receiver.rpm
    speed = obd_receiver.speed
    if rpm >= 2500 or speed >= 65:
        speed35 = speed > 35
        valve.open_valve()
        return

    if (speed <= 35 and speed35) or rpm <= 1200:
        speed35 = False
        valve.close_valve()
        return

    if speed > 35:
        speed35 = True


obd_abnormal = True
wpa_reset = False


def monitor(obd_receiver):
    global obd_abnormal
    global wpa_reset
    try:
        duration = time.time() - obd_receiver.lastReceiveTime
        if duration >= 30:
            if not obd_abnormal:
                obd_abnormal = True
                print("no data received for 30 seconds, open the valve")
            obd_receiver.rpm = 0
            obd_receiver.speed = 0

            # reset wifi when abnormal for 60 seconds
            if duration >= 60 and not wpa_reset:
                wpa_reset = True
                print("abnormal for 1 min, try to reset wpa")
                subprocess.call("wpa_cli -i wlan0 reconfigure", shell=True)

            # reboot when abnormal for 120 seconds
            if duration >= 120:
                print("abnormal for 2 mins, reboot device")
                subprocess.call("reboot", shell=True)

            valve.open_valve()
            return
        sync(obd_receiver)
        obd_abnormal = False
        wpa_reset = False
    except Exception as e:
        print(e)


if __name__ == '__main__':
    receiver = ObdReceiver()
    receiver.start()


    # BroadCastTest().start()

    while True:
        print("rpm=%d, speed=%d" % (receiver.rpm, receiver.speed))
        # monitor(receiver)
        time.sleep(2)
