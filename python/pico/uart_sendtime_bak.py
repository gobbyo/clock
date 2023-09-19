import syncRTC
import picowifi
from machine import Pin
import time
from dht11 import DHT11
import logs
import config
import json
import urequests
import secrets
from servocolons import servoColonsDisplay

maxAttempts = 2
syncWifi = 60 #minutes
dailySyncTime = "1200"  #default
elapsedwaitSyncHumidTemp = 0 #seconds
elapsedwaitDate = 15 #seconds
elapsedwaitTemp = 25 #seconds
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
    if hour == 0:
        hour = 12
    h = strhour = "{0:02}".format(hour)
    if strhour[0] == "0":
        strhour = "E" + h[1]
    return strhour

def setOutdoorTemp(conf):
    try:
        g = urequests.get("http://api.ipstack.com/134.201.250.155?access_key=be774cdbc70c022d8cc7c9e10fc3823f&fields=latitude,longitude")
        geo = json.loads(g.content)
        r = urequests.get("https://api.open-meteo.com/v1/forecast?latitude={0}&longitude={1}&current_weather=true&hourly=relativehumidity_2m".format(geo['latitude'],geo['longitude']))
        j = json.loads(r.content)
        temperature = j['current_weather']['temperature']
        conf.write("tempoutdoor",round(32+(9/5*temperature)))
        print("tempoutdoor = {0}".format(round(32+(9/5*temperature))))
        humidity = j['hourly']['relativehumidity_2m'][0]
        conf.write("humidoutdoor",humidity)
        print("humidoutdoor = {0}".format(humidity))
    except Exception as e:
        log.write("Exception: {}".format(e))
    finally:
        time.sleep(1)

def setIndoorTemp(conf, sensor):
    temp = 0
    humid = 0

    readtempattempts = 5
    while readtempattempts > 0:
        try:
            switch.on()
            time.sleep(1)
            sensor.measure()
            temp = round(sensor.temperature)
            humid = round(sensor.humidity)
            if temp > 0 and humid > 0:
                conf.write("tempreading",temp)
                log.write("tempreading = {0}".format(temp))
                conf.write("humidreading",humid)
                log.write("humidreading = {0}".format(humid))
                switch.off()
                readtempattempts = 1
                log.write("Finished recording temp/humid sensor")
        except Exception as e:
            log.write("Exception: {}".format(e))
        finally:
            switch.off()
            readtempattempts -=1
            time.sleep(1)

def main():
    baudrate = [9600, 19200, 38400, 57600, 115200]
    uarttime = machine.UART(0, baudrate[0], tx=machine.Pin(12), rx=machine.Pin(13))
    uarttime.init(baudrate[0], bits=8, parity=None, stop=1)
    global log
    log = logs.logger("sendtime.log", 4096)
    global tempsensorpin
    tempsensorpin = Pin(20, Pin.OUT, pull=Pin.PULL_DOWN)
    sensor = DHT11(tempsensorpin)
    global switch
    switch = Pin(0, Pin.OUT,value=0)
    colons = servoColonsDisplay()
    
    try:
        global currentTime

        wifi = picowifi.hotspot(secrets.usr, secrets.pwd)
        
        while not wifi.connectWifi():
            time.sleep(5)
        
        log.write("Connected to WiFi")
        elapsedseconds = 0
        waitforwifi = 0
        sync = syncRTC.syncRTC()
        sync.syncclock()
        currentTime = "{0}{1:02}".format(formathour(sync.rtc.datetime()[4]), sync.rtc.datetime()[5])
        conf = config.Config("config.json")
        print("setting outdoor temp")
        setOutdoorTemp(conf)
        print("setting indoor temp")
        setIndoorTemp(conf, sensor)

        while True:
            log.write("elapsed seconds = {0}".format(elapsedseconds))

            #display time
            if (elapsedseconds < elapsedwaitSyncHumidTemp) or (elapsedseconds >= elapsedwaitTime):
                
                if waitforwifi >= syncWifi:
                    connectattempts = maxAttempts
                    while connectattempts > 0:
                        if wifi.connectWifi():
                            log.write("Connected to WiFi Hotspot")
                            log.write("URL: {0}".format(wifi.url))
                            sync.syncclock()
                            setOutdoorTemp(conf)
                            waitforwifi = -1
                            break
                        time.sleep(5)
                        connectattempts -= 1
                
                waitforwifi += 1
                print("waitforwifi = {0}".format(waitforwifi))
                currentTime = "{0}{1:02}".format(formathour(sync.rtc.datetime()[4]), sync.rtc.datetime()[5])
                b = bytearray(currentTime, 'utf-8')
                uarttime.write(b)
                log.write("sent UART = {0}".format(b))
                log.write("currentTime = {0}".format(currentTime))
                colons.extend(True, True)

            #display date
            if (elapsedseconds >= elapsedwaitDate) and (elapsedseconds < elapsedwaitTemp):
                currentDate = "{0:02}{1:02}".format(sync.rtc.datetime()[1], sync.rtc.datetime()[2])
                b = bytearray(currentDate, 'utf-8')
                uarttime.write(b)
                log.write("sent UART = {0}".format(b))
                colons.retract(True, True)
                log.write("currentDate = {0}".format(currentDate))
                time.sleep(2)
                uarttime.write(b)
                while (elapsedseconds < elapsedwaitTemp):
                    elapsedseconds = round(sync.rtc.datetime()[6])
                    log.write("elapsed seconds = {0}".format(elapsedseconds))
                    time.sleep(1)

            #display temp
            if (elapsedseconds >= elapsedwaitTemp) and (elapsedseconds < elapsedwaitHumid):
                showIndoorTemp = conf.read("showIndoorTemp")
                if showIndoorTemp == 1:
                    temp = conf.read("tempreading")
                    curtemp = "{0:02}AD".format(round((temp*1.8)+32))
                    b = bytearray(curtemp, 'utf-8')                    
                    uarttime.write(b)
                    colons.extend(True, False)
                    log.write("sent UART = {0}".format(b))
                    log.write("Indoor Temperature: {0}".format(curtemp))
                else:
                    temp = conf.read("tempoutdoor")
                    curtemp = "{0:02}AD".format(temp)
                    b = bytearray(curtemp, 'utf-8')                    
                    uarttime.write(b)
                    colons.extend(False, True)
                    log.write("sent UART = {0}".format(b))
                    log.write("Outdoor Temperature: {0}".format(curtemp))
                    time.sleep(2)
                    uarttime.write(b)
                while (elapsedseconds < elapsedwaitHumid):
                    elapsedseconds = round(sync.rtc.datetime()[6])
                    log.write("elapsed seconds = {0}".format(elapsedseconds))
                    time.sleep(1)

            #display humid
            if (elapsedseconds >= elapsedwaitHumid) and (elapsedseconds < elapsedwaitTime):
                showIndoorTemp = conf.read("showIndoorTemp")
                if showIndoorTemp == 1:
                    humid = conf.read("humidreading")
                    curhumid = "{0}AB".format(humid)
                    b = bytearray(curhumid, 'utf-8')                    
                    uarttime.write(b)
                    colons.extend(True, False)
                    log.write("sent UART = {0}".format(b))
                    log.write("Indoor Humidity: {0}".format(humid))
                    conf.write("showIndoorTemp",0)
                    time.sleep(2)
                    uarttime.write(b)
                    setIndoorTemp(conf, sensor)
                else:
                    temp = conf.read("humidoutdoor")
                    curtemp = "{0:02}AB".format(temp)
                    b = bytearray(curtemp, 'utf-8')                    
                    uarttime.write(b)
                    colons.extend(False, True)
                    log.write("sent UART = {0}".format(b))
                    log.write("Outdoor Humidity: {0}".format(curtemp))
                    conf.write("showIndoorTemp",1)
                    time.sleep(2)
                    uarttime.write(b)
                while (elapsedseconds < elapsedwaitTime):
                    elapsedseconds = round(sync.rtc.datetime()[6])
                    log.write("elapsed seconds = {0}".format(elapsedseconds))
                    time.sleep(1)

            elapsedseconds = round(sync.rtc.datetime()[6])
            time.sleep(1)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        #sync.__del__()
        print('Done')

if __name__ == "__main__":
    main()