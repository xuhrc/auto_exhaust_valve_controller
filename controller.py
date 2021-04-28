import time
import elm327
import sys
import valve
import obd_udp_receiver


def current_milli_time():
    return round(time.time() * 1000)


if __name__ == '__main__':
    # using artsure OBDII device
    # init the receiver threaq
    # receiver = obd_udp_receiver.ObdReceiver()
    # receiver.start()

    while True:
        try:
            current = current_milli_time()
            # using artsure OBDII device
            # obd_udp_receiver.monitor(receiver)

            # using elm327 wifi device
            elm327.monitor()

            cost = current_milli_time() - current
        except Exception as e:
            print('monitor loop failed')
            print(e)
        time.sleep(0.1)
        sys.stdout.flush()
        sys.stderr.flush()
