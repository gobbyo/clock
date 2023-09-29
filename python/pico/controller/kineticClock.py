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
        self._uart = machine.UART(0, baudRate[0], tx=machine.Pin(uartTxPin), rx=machine.Pin(uartRxPin))
        self._uart.init(baudRate[0], bits=8, parity=None, stop=1)
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
        self._uart.write(b)
        time.sleep(1)
        self._colons.retract(True, True)
        time.sleep(1)
        b = bytearray('4FFFFF', 'utf-8')
        self._uart.write(b)
        time.sleep(2)

    def _sendDisplayUART(self, data):
        pause = 0.25
        if self.motion.value() == 1:
            pause = 0.75
        i = 3
        while i >= 0:
            d = "{0}{1}".format(i,data[1:6])
            b = bytearray(d, 'utf-8')
            self._uart.write(b)
            print("UART = {0}".format(b))
            time.sleep(pause)
            i -= 1
            
    def motion(self):
        curMotion = self._motion.value()
        if self._lastMotion != curMotion:
            if curMotion == 0:
                print("fast digit change speed")
                self._uart.write(bytearray('41FFF0', 'utf-8'))
            else:
                print("slow digit change speed")
                self._uart.write(bytearray('41FFF1', 'utf-8'))

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
        h = strHour = "{0:02}".format(hour)
        if strHour[0] == "0":
            strHour = "E" + h[1]
        return strHour

    def setOutdoorTemp(self, conf):
        print("kineticClock.setOutdoorTemp()")
        try:
            self._connectedLED.on()
            lat = conf.read("lat")
            lon = conf.read("lon")
            r = urequests.get("https://api.open-meteo.com/v1/forecast?latitude={0}&longitude={1}&current_weather=true&hourly=relativehumidity_2m".format(lat,lon))
            j = json.loads(r.content)
            temperature = j['current_weather']['temperature']
            temp = round(float(temperature))
            conf.write("tempoutdoor",temp)
            print("temp sensor outdoor = {0}".format(temp))
            humidity = j['hourly']['relativehumidity_2m'][0]
            humid = round(float(humidity))
            conf.write("humidoutdoor",humid)
            print("humidity sensor outdoor = {0}".format(humid))
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

                #exception may be thrown if sensor is not ready
                self._sensor.measure()

                temp = round(self._sensor.temperature)
                humid = round(self._sensor.humidity)
                conf.write("tempreading",temp)
                print("temp sensor indoor = {0}".format(temp))
                conf.write("humidreading",humid)
                print("humid sensor indoor = {0}".format(humid))

                #gracefully exit the while loop should the sensor read correctly
                readTempAttempts = 1
            except Exception as e:
                print("Exception: {}".format(e))
            finally:
                self._switch.off()
                readTempAttempts -= 1

    def displayTime(self, sync):
        print("kineticClock.displayTime()")
        self._colons.extend(True, True)     
        currentTime = "40{0}{1:02}".format(self.formatHour(sync.rtc.datetime()[4]), sync.rtc.datetime()[5])
        print("display time = {0}".format(currentTime[2:4]))
        self._sendDisplayUART(currentTime)
    
    def displayDate(self):
        print("kineticClock.displayDate()")   
        self._colons.retract(True, True)            
        currentDate = "40{0:02}{1:02}".format(self._sync.rtc.datetime()[1], self._sync.rtc.datetime()[2])
        print("display date = {0}".format(currentDate[2:4]))
        self._sendDisplayUART(currentDate)
    
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
        
        tempCF = conf.read("tempCF")
        if tempCF == "F":
            p = round((temp*1.8)+32)
        else:
            p = temp
        #negative temperatures are displayed without the minus sign,
        #e.g. -12 degrees becomes 12 degrees
        if p < 0:
            p *= -1
        t = "{0}".format(p)
        #temperatures over 99 degrees are displayed without the first digit,
        #e.g. 102 degrees becomes 02 degrees
        if len(t) > 2:
            t = t[1:]
        if tempCF == "F":
            curTemp = "40{0:02}AD".format(int(t))
        else:
            curTemp = "40{0:02}AC".format(int(t))
        
        print("display temp = {0}".format(curTemp))
        self._sendDisplayUART(curTemp)
        

    def displayHumidity(self, conf):
        print("kineticClock.displayHumidity()")
        displayIndoorTemp = conf.read("displayIndoorTemp")
        if displayIndoorTemp == 1:
            h = conf.read("humidreading")
            self._colons.extend(True, False)
            curHumid = "40{0}AB".format(h)
            print("display indoor humidity = {0}".format(curHumid))
            self._sendDisplayUART(curHumid)
            conf.write("displayIndoorTemp",0)
        else:
            self._colons.extend(False, True)
            h = conf.read("humidoutdoor")
            curHumid = "40{0:02}AB".format(h)
            print("display outdoor humidity = {0}".format(curHumid))
            self._sendDisplayUART(curHumid)
            conf.write("displayIndoorTemp",1)