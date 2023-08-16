import syncRTC
import hotspot
import machine
import json
import time

maxAttempts = 3
dailySyncTime = "1200"  #todo: make this configurable

def testsegments(uarttime):
    for i in range(0,10):
        s = "{0:02d}{1:02d}".format(i+(i*10),i+(i*10))
        print(s)
        b = bytearray(s, 'utf-8')
        machine.uarttime.write(b)
        time.sleep(5)

    b = bytearray("cccc", 'utf-8')
    machine.uarttime.write(b)
    time.sleep(7)

def syncTime(sync):
    print("syncTime()")
    i = 0
    while not sync.connectWiFi():
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
        dailySyncTime = currentTime = "1915"
        while True:
            if currentTime == dailySyncTime:
                syncTime(sync)
            j = json.dumps(sync.rtc.datetime())

            if(len(j) < 256):
                currentTime = "{0:02d}{1:02d}".format(sync.rtc.datetime()[4], sync.rtc.datetime()[5])
                print(currentTime)
                b = bytearray(currentTime, 'utf-8')
                uarttime.write(b)
                time.sleep(5)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        sync.__del__()
        print('Done')

if __name__ == "__main__":
    main()