import syncRTC
import hotspot
import machine
import json
import time
import config

maxAttempts = 3
dailySyncTime = "1200"  #default

def syncTime(sync, ssid, pwd):
    print("syncTime()")
    i = 0
    while not sync.connectWiFi(ssid, pwd):
        time.sleep(5)
        if i > maxAttempts:
            raise("Unable to connect to WiFi")
        i += 1

    i = 0
    while not sync.syncclock():
        time.sleep(5)
        if i > maxAttempts:
            raise Exception("Failed to call web APIs")
        i += 1

def main():
    baudrate = [9600, 19200, 38400, 57600, 115200]
    uarttime = machine.UART(0, baudrate[0], tx=machine.Pin(0), rx=machine.Pin(1))
    uarttime.init(baudrate[0], bits=8, parity=None, stop=1)
    #rtc = machine.RTC()

    wifi = hotspot.hotspot("picowclock","12oclock")
    wifi.run()
    ssid = wifi.ssid
    pwd = wifi.pwd

    try:
        sync = syncRTC.syncRTC()
        conf = config.config("")
        stime = conf.read("synctime")
        dailySyncTime = currentTime = conf.read("synctime")
        prevSync = False
        while True:
            if (int(currentTime) == int(dailySyncTime)):
                if prevSync == False:
                    syncTime(sync, ssid, pwd)
                prevSync = True
            else:
                prevSync = False
            j = json.dumps(sync.rtc.datetime())

            if(len(j) < 256):
                currentTime = "{0:02}{1:02}".format(sync.rtc.datetime()[4], sync.rtc.datetime()[5])
                b = bytearray(currentTime, 'utf-8')
                uarttime.write(b)
                #machine.deepsleep(50000)
                time.sleep(5)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        sync.__del__()
        print('Done')

if __name__ == "__main__":
    main()