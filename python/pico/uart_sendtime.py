import syncRTC
from machine import Pin, UART
import json
import time

maxAttempts = 3

def main():
    baudrate = [9600, 19200, 38400, 57600, 115200]
    uarttime = UART(0, baudrate[0], tx=Pin(0), rx=Pin(1))
    uarttime.init(baudrate[0], bits=8, parity=None, stop=1)  

    i = 0
    sync = syncRTC.syncRTC()
    while not sync.connectWiFi():
        time.sleep(5)
        if i > maxAttempts:
            raise Exception("Unable to connect to WiFi")
        i += 1

    while not sync.syncclock():
        time.sleep(5)
        if i > maxAttempts:
            raise Exception("Unable to connect to WiFi")
        i += 1

    try:
        while True:
            j = json.dumps(sync.rtc.datetime())

            if(len(j) < 256):
                s = "{0:02d}{1:02d}".format(sync.rtc.datetime()[4], sync.rtc.datetime()[5])
                print(s)
                b = bytearray(s, 'utf-8')
                uarttime.write(b)
                time.sleep(5)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        sync.__del__()
        print('Done')

if __name__ == "__main__":
    main()