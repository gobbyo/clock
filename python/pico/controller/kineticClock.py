import syncRTC
import picowifi
import machine
import time
from dht11 import DHT11
import json
import urequests
import secrets
from servocolons import servoColonsDisplay

motionPin = const(6)
hour24TimePin = const(7)
tempSensorPin = const(20)
tempSwitchPin = const(0)
disconnectedLEDpin = const(18)
connectedLEDpin = const(19)
uartTxPin = const(12)
uartRxPin = const(13)

class kineticClock():
    def __init__(self, conf) -> None:
        print("kineticClock.__init__()")

        baudRate = [9600, 19200, 38400, 57600, 115200]

        self._connectedLED = machine.Pin(connectedLEDpin, machine.Pin.OUT)
        self._disconnectedLED = machine.Pin(disconnectedLEDpin, machine.Pin.OUT)
        self._uartTime = machine.UART(0, baudRate[0], tx=machine.Pin(uartTxPin), rx=machine.Pin(uartRxPin))
        self._uartTime.init(baudRate[0], bits=8, parity=None, stop=1)
        self._sensor = DHT11(machine.Pin(tempSensorPin, machine.Pin.OUT, pull=machine.Pin.PULL_DOWN))
        self._motion = machine.Pin(motionPin, machine.Pin.IN, machine.Pin.PULL_UP)
        self._display24Hour = machine.Pin(hour24TimePin, machine.Pin.IN, machine.Pin.PULL_UP)
        self._switch = machine.Pin(tempSwitchPin, machine.Pin.OUT,value=0)
        self._colons = servoColonsDisplay(conf)
        self._currentTime = "{0}{1:02}".format(0, 0)
        self._wifi = picowifi.hotspot(secrets.usr, secrets.pwd)
        self._sync = syncRTC.syncRTC()
        self._lastMotion = 0
    
    def __del__(self):
        print("kineticClock.__del__()")
        b = bytearray('40EEEE', 'utf-8')
        self._uartTime.write(b)
        time.sleep(1)
        self._colons.retract(True, True)
        b = bytearray('1FFFFF', 'utf-8')
        self._uartTime.write(b)
        time.sleep(2)

    def motion(self):
        #print("kineticClock.motion()")
        curMotion = self._motion.value()
        #print("curMotion = {0}".format(curMotion))
        if self._lastMotion != curMotion:
            if curMotion == 0:
                print("motion off")
                self._uartTime.write(bytearray('41FFF0', 'utf-8'))
                print("curMotion = {0}".format(curMotion))
            else:
                print("motion on")
                self._uartTime.write(bytearray('41FFF1', 'utf-8'))
                print("curMotion = {0}".format(curMotion))

            self._lastMotion = curMotion
        return curMotion
    
    def connectWifi(self):
        connected = False
        self._disconnectedLED.on()
        while not connected:
            connected = self._wifi.connectWifi()
            time.sleep(1)
            self._disconnectedLED.off()
            time.sleep(1)
            self._disconnectedLED.on()
        if connected:
            print("Connected to WiFi")
            self._disconnectedLED.off()
            self._connectedLED.on()
            time.sleep(1)
            self._connectedLED.off()
        else:
            print("NOT Connected to WiFi")
        return connected

    def setLatLon(self, conf):
        try:
            print("external ip address = {0}".format(self._sync.externalIPaddress))
            g = urequests.get("http://ip-api.com/json/{0}".format(self._sync.externalIPaddress))
            geo = json.loads(g.content)
            conf.write("lat",geo['lat'])
            conf.write("lon",geo['lon'])
            print("lat = {0}".format(geo['lat']))
            print("lon = {0}".format(geo['lon']))
        except Exception as e:
            print("Exception: {}".format(e))
        finally:
            time.sleep(1)
            self._connectedLED.off()
            
    def syncClock(self):
        print("kineticClock.syncClock()")
        self._connectedLED.on()
        try:
            self._sync.syncclock()
        except Exception as e:
            print("Exception: {}".format(e))
        finally:
            self._connectedLED.off()
            
    def formatHour(self, hour):
        display24Hour = self._display24Hour.value()
        if display24Hour == 0:
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
            self._connectedLED.on()
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
            self._connectedLED.off()

    def setIndoorTemp(self,conf):
        print("kineticClock.setIndoorTemp()")
        temp = 0
        humid = 0
        readTempAttempts = 5
        while readTempAttempts > 0:
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
                    readTempAttempts = 1
                    print("Finished recording temp/humid sensor")
            except Exception as e:
                print("Exception: {}".format(e))
            finally:
                self._switch.off()
                readTempAttempts -=1
                time.sleep(1)

    def displayTime(self, sync):
        print("kineticClock.displayTime()")
        self._colons.extend(True, True)
        currentTime = "40{0}{1:02}".format(self.formatHour(sync.rtc.datetime()[4]), sync.rtc.datetime()[5])
        print("currentTime = {0}".format(currentTime))
        b = bytearray(currentTime, 'utf-8')
        self._uartTime.write(b)
        time.sleep(1)
    
    def displayDate(self):
        print("kineticClock.displayDate()")   
        self._colons.retract(True, True)            
        currentDate = "40{0:02}{1:02}".format(self._sync.rtc.datetime()[1], self._sync.rtc.datetime()[2])
        print("currentDate = {0}".format(currentDate))
        b = bytearray(currentDate, 'utf-8')
        self._uartTime.write(b)
        time.sleep(1)
    
    def displayTemp(self,conf):
        print("kineticClock.displayTemp()")
        displayIndoorTemp = conf.read("displayIndoorTemp")
        if displayIndoorTemp == 1:
            self._colons.extend(True, False)
            print("display indoor temp")
            temp = conf.read("tempreading")
        else:
            self._colons.extend(False, True)
            print("display outdoor temp")
            temp = conf.read("tempoutdoor")
        
        p = round((temp*1.8)+32)
        if p < 0:
            p *= -1
        t = "{0}".format(p)
        if len(t) > 2:
            t = t[1:]
        curTemp = "40{0:02}AD".format(int(t))
        b = bytearray(curTemp, 'utf-8')                    
        self._uartTime.write(b)
        print("temp = {0}".format(curTemp))
        time.sleep(1)

    def displayHumidity(self, conf):
        print("kineticClock.displayHumidity()")
        displayIndoorTemp = conf.read("displayIndoorTemp")
        if displayIndoorTemp == 1:
            h = conf.read("humidreading")
            self._colons.extend(True, False)
            curHumid = "40{0}AB".format(h)
            print("indoor humidity = {0}".format(curHumid))
            b = bytearray(curHumid, 'utf-8')                    
            self._uartTime.write(b)
            time.sleep(1)
            conf.write("displayIndoorTemp",0)
        else:
            h = conf.read("humidoutdoor")
            self._colons.extend(False, True)
            curHumid = "40{0:02}AB".format(h)
            print("outdoor humidity = {0}".format(curHumid))
            b = bytearray(curHumid, 'utf-8')                    
            self._uartTime.write(b)
            #log.write("sent UART = {0}".format(b))
            time.sleep(1)
            conf.write("displayIndoorTemp",1)