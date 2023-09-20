import syncRTC
import picowifi
import machine
import time
from dht11 import DHT11
import json
import urequests
import secrets
from servocolons import servoColonsDisplay

tempsensorpin = const(20)
tempswitchpin = const(0)
uartTxPin = const(12)
uartRxPin = const(13)

class kineticClock():
    def __init__(self, conf) -> None:
        print("kineticClock.__init__()")

        baudrate = [9600, 19200, 38400, 57600, 115200]

        self._maxAttemps = 2
        self._elapsedwaitSyncHumidTemp = 5 #seconds
        self._elapsedwaitDate = 20 #seconds
        self._elapsedwaitTemp = 30 #seconds
        self._elapsedwaitHumid = 40 #seconds
        self._elapsedwaitTime = 50 #seconds

        self._uarttime = machine.UART(0, baudrate[0], tx=machine.Pin(uartTxPin), rx=machine.Pin(uartRxPin))
        self._uarttime.init(baudrate[0], bits=8, parity=None, stop=1)
        self._sensor = DHT11(machine.Pin(tempsensorpin, machine.Pin.OUT, pull=machine.Pin.PULL_DOWN))
        self._switch = machine.Pin(tempswitchpin, machine.Pin.OUT,value=0)
        self._colons = servoColonsDisplay(conf)
        self._currentTime = "{0}{1:02}".format(0, 0)
        self._wifi = picowifi.hotspot(secrets.usr, secrets.pwd)
        self._sync = syncRTC.syncRTC()
    
    def __del__(self):
        print("kineticClock.__del__()")
        b = bytearray("{EEEE}", 'utf-8')
        self._uarttime.write(b)
        time.sleep(1)
        self._colons.retract(True, True)
        time.sleep(2)

    def connectWifi(self, conf):
        connected = False
        while not connected:
            connected = self._wifi.connectWifi()
            time.sleep(5)  
        if connected:
            print("Connected to WiFi")
        else:
            print("NOT Connected to WiFi")
        return connected

    def syncClock(self, conf):
        self._sync.syncclock()
        print("kineticClock.syncClock()")
        print("external ip address = {0}".format(self._sync.externalIPaddress))
        g = urequests.get("http://ip-api.com/json/{0}".format(self._sync.externalIPaddress))
        geo = json.loads(g.content)
        conf.write("lat",geo['lat'])
        conf.write("lon",geo['lon'])
        print("lat = {0}".format(geo['lat']))
        print("lon = {0}".format(geo['lon']))
        
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
        print("kineticClock.setOutdoorTemp()")
        try:
            lat = conf.read("lat")
            lon = conf.read("lon")
            r = urequests.get("https://api.open-meteo.com/v1/forecast?latitude={0}&longitude={1}&current_weather=true&hourly=relativehumidity_2m".format(lat,lon))
            j = json.loads(r.content)
            temperature = j['current_weather']['temperature']
            conf.write("tempoutdoor",round(32+(9/5*temperature)))
            print("tempoutdoor = {0}".format(round(32+(9/5*temperature))))
            humidity = j['hourly']['relativehumidity_2m'][0]
            conf.write("humidoutdoor",humidity)
            print("humidoutdoor = {0}".format(humidity))
        except Exception as e:
            print("Exception: {}".format(e))
        finally:
            time.sleep(1)

    def setIndoorTemp(self,conf):
        print("kineticClock.setIndoorTemp()")
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
                    print("tempreading = {0}".format(temp))
                    conf.write("humidreading",humid)
                    print("humidreading = {0}".format(humid))
                    self._switch.off()
                    readtempattempts = 1
                    print("Finished recording temp/humid sensor")
            except Exception as e:
                print("Exception: {}".format(e))
            finally:
                self._switch.off()
                readtempattempts -=1
                time.sleep(1)

    def displayTime(self, sync, militaryTime):
        print("kineticClock.displayTime()")
        currentTime = "{0}{1:02}".format(self.formathour(sync.rtc.datetime()[4]), sync.rtc.datetime()[5])
        b = bytearray(currentTime, 'utf-8')
        self._uarttime.write(b)
        time.sleep(1)
        self._colons.extend(True, True)
    
    def displayDate(self):
        print("kineticClock.displayDate()")               
        currentDate = "{0:02}{1:02}".format(self._sync.rtc.datetime()[1], self._sync.rtc.datetime()[2])
        b = bytearray(currentDate, 'utf-8')
        self._uarttime.write(b)
        time.sleep(1)
        self._colons.retract(True, True)
    
    def displayTemp(self,conf):
        print("kineticClock.displayTemp()")
        displayIndoorTemp = conf.read("displayIndoorTemp")
        if displayIndoorTemp == 1:
            temp = conf.read("tempreading")
            curtemp = "{0:02}AD".format(round((temp*1.8)+32))
            b = bytearray(curtemp, 'utf-8')                    
            self._uarttime.write(b)
            time.sleep(1)
            self._colons.extend(True, False)
        else:
            temp = conf.read("tempoutdoor")
            curtemp = "{0:02}AD".format(temp)
            b = bytearray(curtemp, 'utf-8')                    
            self._uarttime.write(b)
            time.sleep(1)
            self._colons.extend(False, True)

    def displayHumidity(self, conf):
        print("kineticClock.displayHumidity()")
        displayIndoorTemp = conf.read("displayIndoorTemp")
        if displayIndoorTemp == 1:
            humid = conf.read("humidreading")
            curhumid = "{0}AB".format(humid)
            b = bytearray(curhumid, 'utf-8')                    
            self._uarttime.write(b)
            time.sleep(1)
            self._colons.extend(True, False)
            conf.write("displayIndoorTemp",0)
        else:
            temp = conf.read("humidoutdoor")
            curtemp = "{0:02}AB".format(temp)
            b = bytearray(curtemp, 'utf-8')                    
            self._uarttime.write(b)
            #log.write("sent UART = {0}".format(b))
            time.sleep(1)
            self._colons.extend(False, True)
            conf.write("displayIndoorTemp",1)