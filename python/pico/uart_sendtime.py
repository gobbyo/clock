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

tempsensorpin = const(20)
tempswitchpin = const(0)
uartTxPin = const(12)
uartRxPin = const(13)

class kineticClock():
    def __init__(self) -> None:
        print("self.__init__()")

        baudrate = [9600, 19200, 38400, 57600, 115200]

        self._maxAttemps = 2
        self._syncWifi = 60 #minutes
        self._dailySyncTime = "1200"  #default
        self._elapsedwaitSyncHumidTemp = 0 #seconds
        self._elapsedwaitDate = 20 #seconds
        self._elapsedwaitTemp = 30 #seconds
        self._elapsedwaitHumid = 40 #seconds
        self._elapsedwaitTime = 50 #seconds

        self._uarttime = machine.UART(0, baudrate[0], tx=machine.Pin(uartTxPin), rx=machine.Pin(uartRxPin))
        self._uarttime.init(baudrate[0], bits=8, parity=None, stop=1)
        self._log = logs.logger("sendtime.log", 4096)
        self._sensor = DHT11(Pin(tempsensorpin, Pin.OUT, pull=Pin.PULL_DOWN))
        self._switch = Pin(tempswitchpin, Pin.OUT,value=0)
        self._colons = servoColonsDisplay()
        self._currentTime = "{0}{1:02}".format(0, 0)
        self._wifi = picowifi.hotspot(secrets.usr, secrets.pwd)
    
    def __del__(self):
        print("self.__del__()")
        b = bytearray("{EEEE}", 'utf-8')
        self._uarttime.write(b)
        time.sleep(2)
        self._colons.extend(True, True)

    def connectWifi(self, conf):
        connected = False
        while not connected:
            connected = self._wifi.connectWifi()
            time.sleep(5)  
        if connected:
            self._log.write("Connected to WiFi")
        else:
            self._log.write("NOT Connected to WiFi")
        return connected

    def formathour(self, hour):
        if hour > 12:
            hour -= 12
        if hour == 0:
            hour = 12
        h = strhour = "{0:02}".format(hour)
        if strhour[0] == "0":
            strhour = "E" + h[1]
        return strhour

    def setOutdoorTemp(self, conf):
        try:
            lat = conf.read("lat")
            lon = conf.read("lon")
            r = urequests.get("https://api.open-meteo.com/v1/forecast?latitude={0}&longitude={1}&current_weather=true&hourly=relativehumidity_2m".format(lat,lon))
            j = json.loads(r.content)
            temperature = j['current_weather']['temperature']
            conf.write("tempoutdoor",round(32+(9/5*temperature)))
            self._log.write("tempoutdoor = {0}".format(round(32+(9/5*temperature))))
            humidity = j['hourly']['relativehumidity_2m'][0]
            conf.write("humidoutdoor",humidity)
            self._log.write("humidoutdoor = {0}".format(humidity))
        except Exception as e:
            self._log.write("Exception: {}".format(e))
        finally:
            time.sleep(1)

    def setIndoorTemp(self,conf):
        temp = 0
        humid = 0

        readtempattempts = 5
        while readtempattempts > 0:
            try:
                self._switch.on()
                time.sleep(1)
                self._sensor.measure()
                temp = round(self._sensor.temperature)
                humid = round(self._sensor.humidity)
                if temp > 0 and humid > 0:
                    conf.write("tempreading",temp)
                    self._log.write("tempreading = {0}".format(temp))
                    conf.write("humidreading",humid)
                    self._log.write("humidreading = {0}".format(humid))
                    self._switch.off()
                    readtempattempts = 1
                    self._log.write("Finished recording temp/humid sensor")
            except Exception as e:
                self._log.write("Exception: {}".format(e))
            finally:
                self._switch.off()
                readtempattempts -=1
                time.sleep(1)

def main():
    try:
        clock = kineticClock()

        elapsedseconds = 0
        waitforwifi = 0
        conf = config.Config("config.json")

        if clock.connectWifi(conf):
            sync = syncRTC.syncRTC()
            sync.syncclock()
            currentTime = "{0}{1:02}".format(clock.formathour(sync.rtc.datetime()[4]), sync.rtc.datetime()[5])  
            print("external ip address = {0}".format(sync.externalIPaddress))
            g = urequests.get("http://ip-api.com/json/{0}".format(sync.externalIPaddress))
            geo = json.loads(g.content)
            conf.write("lat",geo['lat'])
            conf.write("lon",geo['lon'])
            clock._log.write("lat = {0}".format(geo['lat']))
            clock._log.write("lon = {0}".format(geo['lon']))

        while True:
            #display time
            if (elapsedseconds > clock._elapsedwaitTime) or (elapsedseconds < clock._elapsedwaitSyncHumidTemp):
                clock._log.write("--display time--")
                clock._log.write("elapsedseconds = {0}".format(elapsedseconds))
                currentTime = "{0}{1:02}".format(clock.formathour(sync.rtc.datetime()[4]), sync.rtc.datetime()[5])
                b = bytearray(currentTime, 'utf-8')
                clock._uarttime.write(b)
                time.sleep(1)
                clock._colons.extend(True, True)
                
                while elapsedseconds < 15:
                    elapsedseconds = round(sync.rtc.datetime()[6])
                    time.sleep(1)
            
            #read temp/humid sensor
            if (elapsedseconds >= clock._elapsedwaitSyncHumidTemp) and (elapsedseconds < clock._elapsedwaitDate):
                clock._log.write("--reading temp sensor--")
                clock._log.write("elapsedseconds = {0}".format(elapsedseconds))
                clock.setIndoorTemp(conf)
                time.sleep(1)
                clock.setOutdoorTemp(conf)
                while (elapsedseconds < clock._elapsedwaitDate):
                    time.sleep(1)
                    elapsedseconds = round(sync.rtc.datetime()[6])

            #display date
            if (elapsedseconds >= clock._elapsedwaitDate) and (elapsedseconds < clock._elapsedwaitTemp):
                clock._log.write("--display date--")
                clock._log.write("elapsedseconds = {0}".format(elapsedseconds))                
                currentDate = "{0:02}{1:02}".format(sync.rtc.datetime()[1], sync.rtc.datetime()[2])
                b = bytearray(currentDate, 'utf-8')
                clock._uarttime.write(b)
                time.sleep(1)
                clock._colons.retract(True, True)

                while (elapsedseconds < clock._elapsedwaitTemp):
                    time.sleep(1)
                    elapsedseconds = round(sync.rtc.datetime()[6])

            #display temp
            if (elapsedseconds >= clock._elapsedwaitTemp) and (elapsedseconds < clock._elapsedwaitHumid):
                clock._log.write("--display temp--")
                clock._log.write("elapsedseconds = {0}".format(elapsedseconds))                
                showIndoorTemp = conf.read("showIndoorTemp")
                if showIndoorTemp == 1:
                    temp = conf.read("tempreading")
                    curtemp = "{0:02}AD".format(round((temp*1.8)+32))
                    b = bytearray(curtemp, 'utf-8')                    
                    clock._uarttime.write(b)
                    time.sleep(1)
                    clock._colons.extend(True, False)
                else:
                    temp = conf.read("tempoutdoor")
                    curtemp = "{0:02}AD".format(temp)
                    b = bytearray(curtemp, 'utf-8')                    
                    clock._uarttime.write(b)
                    time.sleep(1)
                    clock._colons.extend(False, True)
                while (elapsedseconds < clock._elapsedwaitHumid):
                    time.sleep(1)
                    elapsedseconds = round(sync.rtc.datetime()[6])

            #display humidity
            if (elapsedseconds >= clock._elapsedwaitHumid) and (elapsedseconds < clock._elapsedwaitTime):
                clock._log.write("--display humidity--")
                clock._log.write("elapsedseconds = {0}".format(elapsedseconds))
                showIndoorTemp = conf.read("showIndoorTemp")
                if showIndoorTemp == 1:
                    humid = conf.read("humidreading")
                    curhumid = "{0}AB".format(humid)
                    b = bytearray(curhumid, 'utf-8')                    
                    clock._uarttime.write(b)
                    time.sleep(1)
                    clock._colons.extend(True, False)
                    conf.write("showIndoorTemp",0)
                else:
                    temp = conf.read("humidoutdoor")
                    curtemp = "{0:02}AB".format(temp)
                    b = bytearray(curtemp, 'utf-8')                    
                    clock._uarttime.write(b)
                    #log.write("sent UART = {0}".format(b))
                    time.sleep(1)
                    clock._colons.extend(False, True)
                    conf.write("showIndoorTemp",1)
                while (elapsedseconds < clock._elapsedwaitTime):
                    time.sleep(1)
                    elapsedseconds = round(sync.rtc.datetime()[6])

            elapsedseconds = round(sync.rtc.datetime()[6])
            print("elapsedseconds = {0}".format(elapsedseconds))
            time.sleep(1)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        #sync.__del__()
        print('Done')

if __name__ == "__main__":
    main()