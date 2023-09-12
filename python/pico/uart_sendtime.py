import syncRTC
import picowifi
from machine import Pin
import time
from dht11 import DHT11
import logs
#import config

maxAttempts = 3
dailySyncTime = "1200"  #default

def showreceive(uart,log):
    time.sleep(1)
    log.write("showreceive() called")
    s = uart.any()
    if s > 0:
        b = bytearray('0000', 'utf-8')
        uart.readinto(b)
        t = b.decode('utf-8')
        log.write("received = {0}".format(t))

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

def formathour(hour):
    if hour > 12:
        hour -= 12
    h = strhour = "{0:02}".format(hour)
    if strhour[0] == "0":
        strhour = "E" + h[1]
    return strhour

def main():
    baudrate = [9600, 19200, 38400, 57600, 115200]
    uarttime = machine.UART(0, baudrate[0], tx=machine.Pin(12), rx=machine.Pin(13))
    uarttime.init(baudrate[0], bits=8, parity=None, stop=1)
    log = logs.logger("sendtime.log", 4096)

    try:
        pin = Pin(28, Pin.OUT, Pin.PULL_DOWN)
        temp = 0
        humid = 0
        wifi = picowifi.hotspot('Clipper','Orcatini')
        
        while not wifi.connectWifi():
            time.sleep(5)
        
        log.write("Connected to WiFi Hotspot")
        elapsedseconds = 0
        waitforwifi = 2
        sync = syncRTC.syncRTC()

        while True:
            log.write("elapsed seconds = {0}".format(elapsedseconds))
            if elapsedseconds < 20 or elapsedseconds >= 40:
                if waitforwifi >= 2:
                    if wifi.connectWifi():
                        log.write("Connected to WiFi Hotspot")
                        log.write("URL: {0}".format(wifi.url))
                        sync.syncclock()
                    waitforwifi = 0
                else:
                    currentTime = "{0}{1:02}".format(formathour(sync.rtc.datetime()[4]), sync.rtc.datetime()[5])
                    b = bytearray(currentTime, 'utf-8')
                    uarttime.write(b)
                    
                    elapsedseconds = round(sync.rtc.datetime()[6])
                    log.write("currentTime = {0}, elapsedseconds = {1}".format(currentTime,elapsedseconds))
                    if elapsedseconds == 0:
                        waitforwifi += 1
                    showreceive(uarttime,log)
                    time.sleep(1)
            else:
                showtemp = True
                try:
                    sensor = DHT11(pin)
                    sensor.measure()
                    temp = round(sensor.temperature)
                    humid = round(sensor.humidity)
                except Exception as e:
                    log.write("Exception: {}".format(e))
                    time.sleep(10)
                    showtemp = False
                finally:
                    elapsedseconds = round(sync.rtc.datetime()[6])
                    log.write("Finished reading temp/humidity sensor")
                    
                if showtemp:
                    curtemp = "{0:02}AD".format(round((temp*1.8)+32))
                    b = bytearray(curtemp, 'utf-8')
                    for i in range(0,10):
                        uarttime.write(b)
                        elapsedseconds = round(sync.rtc.datetime()[6])
                        log.write("Temperature: {0}, elapsedseconds = {1}".format(curtemp,elapsedseconds))
                        showreceive(uarttime,log)
                        time.sleep(1)
                        
                    humid = "{0:02}AB".format(humid)
                    b = bytearray(humid, 'utf-8')
                    for i in range(0,10):
                        uarttime.write(b)
                        elapsedseconds = round(sync.rtc.datetime()[6])
                        log.write("Humidity: {0}, elapsedseconds = {1}".format(humid,elapsedseconds))
                        showreceive(uarttime,log)
                        time.sleep(1)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        #sync.__del__()
        print('Done')

if __name__ == "__main__":
    main()