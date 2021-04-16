from threading import Thread
import socket
import time
from random import randint


class BroadCastTest(Thread):
    def run(self):
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while True:
            sender.sendto("ATZR{:05d},S{:03d}".format(randint(1000, 2000), randint(35, 100)), ('<broadcast>', 50000))
            time.sleep(0.25)


if __name__ == '__main__':
    BroadCastTest().start()
