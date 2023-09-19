import syncRTC
import picowifi
import machine
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

class timeEnum():
    year = 0
    month = 1
    day = 2
    weekday = 3
    hours = 4
    minutes = 5
    seconds = 6
    subseconds = 7

class kineticClock():
    def __init__(self) -> None:
        print("self.__init__()")

        baudrate = [9600, 19200, 38400, 57600, 115200]

        self._maxAttemps = 2
        self._elapsedwaitSyncHumidTemp = 5 #seconds
        self._elapsedwaitDate = 20 #seconds
        self._elapsedwaitTemp = 30 #seconds
        self._elapsedwaitHumid = 40 #seconds
        self._elapsedwaitTime = 50 #seconds

        self._uarttime = machine.UART(0, baudrate[0], tx=machine.Pin(uartTxPin), rx=machine.Pin(uartRxPin))
        self._uarttime.init(baudrate[0], bits=8, parity=None, stop=1)
        self._log = logs.logger("sendtime.log", 4096)
        self._sensor = DHT11(machine.Pin(tempsensorpin, machine.Pin.OUT, pull=machine.Pin.PULL_DOWN))
        self._switch = machine.Pin(tempswitchpin, machine.Pin.OUT,value=0)
        self._colons = servoColonsDisplay()
        self._currentTime = "{0}{1:02}".format(0, 0)
        self._wifi = picowifi.hotspot(secrets.usr, secrets.pwd)
        self._sync = syncRTC.syncRTC()
    
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

    def syncClock(self, conf):
        self._sync.syncclock()
        print("external ip address = {0}".format(self._sync.externalIPaddress))
        g = urequests.get("http://ip-api.com/json/{0}".format(self._sync.externalIPaddress))
        geo = json.loads(g.content)
        conf.write("lat",geo['lat'])
        conf.write("lon",geo['lon'])
        self._log.write("lat = {0}".format(geo['lat']))
        self._log.write("lon = {0}".format(geo['lon']))
        
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

    def displayTime(self, sync):
        self._log.write("--display time--")
        currentTime = "{0}{1:02}".format(self.formathour(sync.rtc.datetime()[4]), sync.rtc.datetime()[5])
        b = bytearray(currentTime, 'utf-8')
        self._uarttime.write(b)
        time.sleep(1)
        self._colons.extend(True, True)
    
    def displayDate(self):
        self._log.write("--display date--")               
        currentDate = "{0:02}{1:02}".format(self._sync.rtc.datetime()[1], self._sync.rtc.datetime()[2])
        b = bytearray(currentDate, 'utf-8')
        self._uarttime.write(b)
        time.sleep(1)
        self._colons.retract(True, True)
    
    def displayTemp(self,conf):
        self._log.write("--display temp--")
        showIndoorTemp = conf.read("showIndoorTemp")
        if showIndoorTemp == 1:
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
        self._log.write("--display humidity--")
        showIndoorTemp = conf.read("showIndoorTemp")
        if showIndoorTemp == 1:
            humid = conf.read("humidreading")
            curhumid = "{0}AB".format(humid)
            b = bytearray(curhumid, 'utf-8')                    
            self._uarttime.write(b)
            time.sleep(1)
            self._colons.extend(True, False)
            conf.write("showIndoorTemp",0)
        else:
            temp = conf.read("humidoutdoor")
            curtemp = "{0:02}AB".format(temp)
            b = bytearray(curtemp, 'utf-8')                    
            self._uarttime.write(b)
            #log.write("sent UART = {0}".format(b))
            time.sleep(1)
            self._colons.extend(False, True)
            conf.write("showIndoorTemp",1)
def main():
    wifischedule = 4 #hours
    temphumidschedule = 2 #minutes
    nextwifischedule = 0
    nexttemphumidschedule = 0

    try:
        clock = kineticClock()

        elapsedseconds = 0
        conf = config.Config("config.json")

        if clock.connectWifi(conf):
            clock.syncClock(conf)
            print("external ip address = {0}".format(clock._sync.externalIPaddress))
            g = urequests.get("http://ip-api.com/json/{0}".format(clock._sync.externalIPaddress))
            geo = json.loads(g.content)
            conf.write("lat",geo['lat'])
            conf.write("lon",geo['lon'])
            clock._log.write("lat = {0}".format(geo['lat']))
            clock._log.write("lon = {0}".format(geo['lon']))
        
        nexttemphumidschedule = (clock._sync.rtc.datetime()[timeEnum.minutes] + temphumidschedule)%60 #minutes
        nextwifischedule = (clock._sync.rtc.datetime()[timeEnum.hours] + wifischedule)%24 #hours

        while True:
            #display time
            if (elapsedseconds > clock._elapsedwaitTime) or (elapsedseconds < clock._elapsedwaitSyncHumidTemp):
                clock.displayTime(clock._sync)
                clock._log.write("elapsedmins = {0}, elapsedseconds = {1}".format(clock._sync.rtc.datetime()[timeEnum.minutes], elapsedseconds))
                
                #sensor measurement
                clock._log.write("nexttemphumidschedule = {0}".format(nexttemphumidschedule))
                if nexttemphumidschedule <= clock._sync.rtc.datetime()[timeEnum.minutes]:
                    nexttemphumidschedule = (clock._sync.rtc.datetime()[timeEnum.minutes] + temphumidschedule)%60 #minutes
                    clock._log.write("--reading temp sensor--")
                    clock.setIndoorTemp(conf)
                    time.sleep(1)
                    clock.setOutdoorTemp(conf)
                    time.sleep(2)
                while elapsedseconds < clock._elapsedwaitSyncHumidTemp:
                    elapsedseconds = round(clock._sync.rtc.datetime()[timeEnum.seconds])
                    time.sleep(1)
                
                #wifi and time sync
                if nextwifischedule <= clock._sync.rtc.datetime()[timeEnum.hours]:
                    nextwifischedule = (clock._sync.rtc.datetime()[timeEnum.hours] + wifischedule)%24 #hours
                    clock._log.write("--wifi and time sync--")
                    if clock.connectWifi(conf):
                        clock.syncClock(conf)
            
            #display date
            if (elapsedseconds >= clock._elapsedwaitDate) and (elapsedseconds < clock._elapsedwaitTemp):
                clock.displayDate()
                clock._log.write("elapsedseconds = {0}".format(elapsedseconds))                
                while (elapsedseconds < clock._elapsedwaitTemp):
                    time.sleep(1)
                    elapsedseconds = round(clock._sync.rtc.datetime()[timeEnum.seconds])

            #display temp
            if (elapsedseconds >= clock._elapsedwaitTemp) and (elapsedseconds < clock._elapsedwaitHumid):
                clock.displayTemp(conf)
                clock._log.write("elapsedseconds = {0}".format(elapsedseconds))                
                while (elapsedseconds < clock._elapsedwaitHumid):
                    time.sleep(1)
                    elapsedseconds = round(clock._sync.rtc.datetime()[timeEnum.seconds])

            #display humidity
            if (elapsedseconds >= clock._elapsedwaitHumid) and (elapsedseconds < clock._elapsedwaitTime):
                clock.displayHumidity(conf)
                clock._log.write("elapsedseconds = {0}".format(elapsedseconds))
                while (elapsedseconds < clock._elapsedwaitTime):
                    time.sleep(1)
                    elapsedseconds = round(clock._sync.rtc.datetime()[timeEnum.seconds])

            elapsedseconds = round(clock._sync.rtc.datetime()[timeEnum.seconds])
            print("elapsedseconds = {0}".format(elapsedseconds))
            time.sleep(1)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        #sync.__del__()
        print('Done')

if __name__ == "__main__":
    main()