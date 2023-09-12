import syncRTC
import picowifi
from machine import Pin
import time
from dht11 import DHT11
import logs
#import config

maxAttempts = 3
dailySyncTime = "1200"  #default
elapsedwaitDate = 20 #seconds
elapsedwaitTemp = 30 #seconds
elapsedwaitHumid = 40 #seconds
elapsedwaitTime = 50 #seconds

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
        global temp
        global humid
        global currentTime

        temp = 0
        humid = 0
        pin = Pin(28, Pin.OUT, Pin.PULL_DOWN)
        wifi = picowifi.hotspot('Clipper','Orcatini')
        
        while not wifi.connectWifi():
            time.sleep(5)
        
        log.write("Connected to WiFi")
        elapsedseconds = 0
        waitforwifi = 2
        sync = syncRTC.syncRTC()
        currentTime = "{0}{1:02}".format(formathour(sync.rtc.datetime()[4]), sync.rtc.datetime()[5])

        while True:
            log.write("elapsed seconds = {0}".format(elapsedseconds))
            showtemp = True

            if (elapsedseconds < elapsedwaitDate) or (elapsedseconds >= elapsedwaitTime):
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
                    log.write("sent UART = {0}".format(b))
                    time.sleep(2)

                    log.write("currentTime = {0}".format(currentTime))
                    if elapsedseconds == 0:
                        waitforwifi += 1
            
            if (elapsedseconds >= elapsedwaitDate) and (elapsedseconds < elapsedwaitTemp):
                currentDate = "{0:02}{1:02}".format(sync.rtc.datetime()[1], sync.rtc.datetime()[2])
                b = bytearray(currentDate, 'utf-8')
                uarttime.write(b)
                log.write("sent UART = {0}".format(b))
                time.sleep(2)
                log.write("currentDate = {0}".format(currentTime))

            if (elapsedseconds >= elapsedwaitTemp) and (elapsedseconds < elapsedwaitHumid):
                try:
                    sensor = DHT11(pin)
                    sensor.measure()
                    temp = round(sensor.temperature)
                    humid = round(sensor.humidity)
                except Exception as e:
                    log.write("Exception: {}".format(e))
                    showtemp = False
                finally:
                    log.write("Finished reading temp sensor")
                
                if showtemp:
                    curtemp = "{0:02}AD".format(round((temp*1.8)+32))
                    b = bytearray(curtemp, 'utf-8')                    
                    uarttime.write(b)
                    log.write("sent UART = {0}".format(b))
                    time.sleep(2)
                    log.write("Temperature: {0}".format(curtemp))

            if (elapsedseconds >= elapsedwaitHumid) and (elapsedseconds < elapsedwaitTime):
                if showtemp:
                    try:
                        sensor = DHT11(pin)
                        sensor.measure()
                        temp = round(sensor.temperature)
                        humid = round(sensor.humidity)
                    except Exception as e:
                        log.write("Exception: {}".format(e))
                        showtemp = False
                    finally:
                        log.write("Finished reading humidity sensor")
                
                    humid = "{0:02}AB".format(humid)
                    b = bytearray(humid, 'utf-8')                    
                    uarttime.write(b)
                    log.write("sent UART = {0}".format(b))
                    time.sleep(2)
                    log.write("Humidity: {0}".format(humid))
            
            elapsedseconds = round(sync.rtc.datetime()[6])

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        #sync.__del__()
        print('Done')

if __name__ == "__main__":
    main()