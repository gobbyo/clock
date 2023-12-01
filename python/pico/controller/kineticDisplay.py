import syncRTC
import picowifi
import machine
import time
from dht11 import DHT11
import json
import urequests
import secrets
import uarttools
from servocolons import servoColonsDisplay
from digitconfigenum import uartCommandEnum

hour24TimePin = const(7)
hybernatePin = const(8)
tempSensorPin = const(20)
tempSwitchPin = const(0)
disconnectedLEDpin = const(18) #red
connectedLEDpin = const(19) #green

# This class is used to control the digit controllers to the display. It contains methods to set the current time, 
# display the current time, display the current date, display the current temperature, display the current humidity, and display the current
# outdoor temperature and humidity. It also contains methods to set the extend and retract angles for each digit.
# The class also contains methods to put the display into a hibernation state when the user changes the toggle switch
# to the "off" position and to wake the display when the user changes the toggle switch to the "on" position.
# The class also contains methods to establish a WiFi connection, obtain the latitude and longitude of the device's
# external IP address, and synchronize the device's internal clock (RTC) with the current time.
class kineticDisplay():
    def __init__(self, conf) -> None:
        print("kineticDisplay.__init__()")

        self._connectedLED = machine.Pin(connectedLEDpin, machine.Pin.OUT)
        self._disconnectedLED = machine.Pin(disconnectedLEDpin, machine.Pin.OUT)
        self._uart = machine.UART(0, uarttools.baudRate[0], tx=machine.Pin(uarttools.uartTxPin), rx=machine.Pin(uarttools.uartRxPin))
        self._uart.init(uarttools.baudRate[0], bits=8, parity=None, stop=1)
        self._sensor = DHT11(machine.Pin(tempSensorPin, machine.Pin.OUT, pull=machine.Pin.PULL_DOWN))
        self._display24Hour = machine.Pin(hour24TimePin, machine.Pin.IN, machine.Pin.PULL_DOWN)
        self._hybernate = machine.Pin(hybernatePin, machine.Pin.IN, machine.Pin.PULL_DOWN)
        self._switch = machine.Pin(tempSwitchPin, machine.Pin.OUT,value=0)
        self._colons = servoColonsDisplay(conf)
        self._currentTime = "{0}{1:02}".format(0, 0)
        self._wifi = picowifi.hotspot(secrets.usr, secrets.pwd)
        self._sync = syncRTC.syncRTC()
    
    def __del__(self):
        print("kineticDisplay.__del__()")
        b = bytearray('4{0}EEEE'.format(uartCommandEnum.time), 'utf-8')
        self._uart.write(b)
        time.sleep(1)
        self._colons.retract(True, True)
        time.sleep(1)
        b = bytearray('4{0}FFFF'.format(uartCommandEnum.reset), 'utf-8')
        self._uart.write(b)
        time.sleep(2)

    #a private method that is used to send data to a display via UART (Universal Asynchronous Receiver/Transmitter), 
    # a common communication protocol in microcontrollers. The method takes a string data as an argument, 
    # converts it into a bytearray in UTF-8 encoding, and then writes this bytearray to the UART. 
    def _sendDisplayUART(self,data):
        b = bytearray(data, 'utf-8')
        self._uart.write(b)

    def admin(self):
        if self._hybernate.value() == 0:
            self._connectedLED.on()
            self._disconnectedLED.on()
            self._wifi.connectAdmin(self)
            self._connectedLED.off()
            self._disconnectedLED.off()

    # This method is used to put the display into a hibernation state when the user changes the toggle switch to the "off" position.
    # The amount of time the digit controllers hybernate is determined by the value in the configuration file--typically 15 seconds.
    # When the switch is turned to its "on" position, the display wakes up and displays the current time.
    def hybernateSwitch(self, conf):
        if self._hybernate.value() == 0:
            print("Hybernate by switch, switch = OFF")
            self._colons.retract(True, True)
            b = bytearray('4{0}EEEE'.format(uartCommandEnum.time), 'utf-8')
            self._uart.write(b)
            
            for i in range(0,3):
                self._disconnectedLED.on()
                time.sleep(0.75)
                self._disconnectedLED.off()
                time.sleep(0.25)
            seconds = int(uarttools.decodeHex(conf.read("hybernate")))
            print("Deep sleep for {0} seconds".format(seconds))
            b = bytearray('4{0}EEEE'.format(uartCommandEnum.time), 'utf-8')
            self._uart.write(b)
            time.sleep(1)
            msg = '46'
            for i in range(0,4):
                msg = msg + uarttools.encodeHex(seconds)
            b = bytearray(msg, 'utf-8')
            self._sendDisplayUART(b)
            while self._hybernate.value() == 0:
                print("Waiting for switch to turn ON")
                self._sendDisplayUART(b)
                for i in range(0,seconds+2):
                    time.sleep(1)
    
    # This method is retrieves the extend angle configuration values for the target digit (0-3).
    # It sends a command to the digit controller to retrieve the extend angles for the target digit.
    # It then enters a loop where it waits for the digit controller to send the angles back via UART.
    # Once the angles are received, they are appended to a list. The loop continues until 7 angles are received.
    # The list of angles is then sorted in ascending order and returned.
    # If the digit controller does not respond after 10 seconds, the method returns an empty list.
    def getExtendAngles(self, digitNumber):
        print("kineticDisplay.getExtendAngles({0})".format(digitNumber))
        b = bytearray('{0}{1}EEEE'.format(digitNumber,uartCommandEnum.txextend), 'utf-8')
        self._uart.write(b)
        print("write uart={0}".format(b))
        angles = []
        i = 0
        k = 0
        while i < 7:
            if k > 100:
                break
            k += 1
            time.sleep(.1)
            if self._uart.any() > 0:
                b = bytearray('000000', 'utf-8')
                self._uart.readinto(b)
                d = str(b.decode('utf-8'))
                print("validate({0}) = {1}".format(d,uarttools.validate(d)))
                if uarttools.validate(d):
                    print("Command = {0}".format(uarttools.decodeHex(d[1])))
                    command = int(uarttools.decodeHex(d[1]))
                    #if(uartCommandEnum.txextend == command) and (digitNumber == int(uarttools.decodeHex(d[0]))):
                    angles.append(d[2:6])
                    i += 1
        angles.sort()

        for i in range(0,len(angles)):
            if len(angles[i]) == 4:
                angles[i] = int(angles[i][1:4])
            else:
                angles[i] = int(angles[i])
            #print("angles = {0}".format(angles[i]))

        return angles

    # This method is retrieves the retract angle configuration values for the target digit (0-3).
    # It sends a command to the digit controller to retrieve the retract angles for the target digit.
    # It then enters a loop where it waits for the digit controller to send the angles back via UART.
    # Once the angles are received, they are appended to a list. The loop continues until 7 angles are received.
    # The list of angles is then sorted in ascending order and returned.
    # If the digit controller does not respond after 10 seconds, the method returns an empty list.
    def getRetractAngles(self, digitNumber):
        print("kineticDisplay.getRetractAngles({0})".format(digitNumber))
        b = bytearray('{0}{1}EEEE'.format(digitNumber,uartCommandEnum.txretract), 'utf-8')
        self._uart.write(b)
        print("write uart={0}".format(b))
        angles = []
        i = 0
        k = 0
        while i < 7:
            if k > 100:
                break
            k += 1
            time.sleep(.1)
            if self._uart.any() > 0:
                b = bytearray('000000', 'utf-8')
                self._uart.readinto(b)
                d = str(b.decode('utf-8'))
                print("validate({0}) = {1}".format(d,uarttools.validate(d)))
                if uarttools.validate(d):
                    print("Command = {0}".format(uarttools.decodeHex(d[1])))
                    command = int(uarttools.decodeHex(d[1]))
                    #if(uartCommandEnum.txretract == command) and (digitNumber == int(uarttools.decodeHex(d[0]))):
                    angles.append(d[2:6])
                    i += 1
        angles.sort()

        for i in range(0,len(angles)):
            if len(angles[i]) == 4:
                angles[i] = int(angles[i][1:4])
            else:
                angles[i] = int(angles[i])
            print("angles = {0}".format(angles[i]))

        return angles

    # This method is used to set the extend and retract angles for a target digit (0-3).
    # It first retrieves the current extend and retract angles for the target digit.
    # It then compares the current angles with the new angles. If the new angles are different from the current angles,
    # It sends a command to the digit controller to set the new angles.
    # It then enters a loop where it waits for the digit controller to send the angles back via UART.
    # once the angles are received, they are appended to a list. The loop continues until 7 angles are received.
    # the list of angles is then sorted in ascending order and returned.
    # if the digit controller does not respond after 10 seconds, the method returns an empty list.
    def setAngles(self, digitNumber, extendAngles, retractAngles):
        for i in range(0,len(extendAngles)):
            print("set extend angle = {0}".format(extendAngles[i]))
            b = bytearray('{0}{1}{2}{3:03}'.format(digitNumber,uartCommandEnum.rxextend,i,extendAngles[i]), 'utf-8')
            self._uart.write(b)
            time.sleep(.1)
        for i in range(0,len(retractAngles)):
            print("set retract angle = {0}".format(retractAngles[i]))
            b = bytearray('{0}{1}{2}{3:03}'.format(digitNumber,uartCommandEnum.rxretract,i,retractAngles[i]), 'utf-8')
            self._uart.write(b)
            time.sleep(.1)
    
    def hybernateTime(self, conf):
        sleep = conf.read("sleep")
        dt = self._sync.rtc.datetime()
        curtime = "{0:02}{1:02}".format(dt[4],dt[5])
        if sleep == curtime:
            print("Hybernate by time, sleep = current time")
            self._colons.retract(True, True)
            b = bytearray('4{0}EEEE'.format(uartCommandEnum.time), 'utf-8')
            self._uart.write(b)
            
            for i in range(0,3):
                self._disconnectedLED.on()
                time.sleep(0.75)
                self._disconnectedLED.off()
                time.sleep(0.25)
            wake = conf.read("wake")
            print("wake = {0}".format(wake))
            j = int(wake)
            i = 0
            if int(wake) > 60:
                i = round(int(wake) / 60)   
                while i > 0:
                    for a in range(0,4):
                        msg = '{0}{1}0060'.format(a, uartCommandEnum.timedhybernation)
                        b = bytearray(msg, 'utf-8')
                        self._sendDisplayUART(b)
                        print("sleep message sent to digit {0}, msg = {1}".format(a,msg))
                    time.sleep((60 * 60) + 5)
                    i -= 1
                j %= 60
            
            if j > 0:
                for a in range(0,4):
                    msg = '{0}{1}0000'.format(a, uartCommandEnum.timedhybernation)
                    msg = msg[0:6-len(str(j))] + str(j)
                    b = bytearray(msg, 'utf-8')
                    self._sendDisplayUART(b)
                    print("sleep message sent to digit {0}, msg = {1}".format(a, msg))
                time.sleep((j * 60)+1)

    # This method establishes a WiFi connection. It first turns on a "disconnected" (red) LED, then enters a loop
    # where it attempts to connect to WiFi. If the connection is not successful, it waits for one second, 
    # turns off the "disconnected" LED, waits for another second, and then turns the "disconnected" LED back 
    # on before trying to connect again. This cycle repeats until a connection is established. Once connected, 
    # it prints a message, turns off the "disconnected" LED, turns on a "connected" (green) LED, waits for a second, 
    # turns off the "connected" LED, and finally returns the connection status.
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

    # This method is used to obtain the latitude and longitude of the device's external IP address.
    # The latitude and longitude are then written to the configuration file and used to obtain the
    # outdoor temperature and humidity.
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
    
    # This method is used to synchronize the device's internal clock (RTC) with the current time.
    def syncClock(self):
        print("kineticDisplay.syncClock()")
        self._connectedLED.on()
        try:
            self._sync.syncclock()
        except Exception as e:
            print("Exception: {}".format(e))
        finally:
            self._connectedLED.off()
    
    # This method is used to set the current time on the display. It first checks to see if the user has selected
    # 12 or 24 hour time. If 12 hour time is selected, it converts the hour to 12 hour time. If 24 hour time is
    # selected, it leaves the hour as is. It then sends the current time to the digit controllers via UART.
    def formatHour(self, hour):
        if self._display24Hour.value() == 1:
            print("display 12 hour time")
            if hour > 12:
                hour -= 12
            if hour == 0:
                hour = 12
        else:
            print("display 24 hour time")
            
        h = strHour = "{0:02}".format(hour)
        if strHour[0] == "0":
            strHour = "E" + h[1]
        return strHour

    # This method is used to set the outdoor temperature and humidity. It first turns on a "connected" (green) LED,
    # then obtains the latitude and longitude of the device's external IP address. It then uses the latitude and
    # longitude to obtain the outdoor temperature and humidity. Finally, it turns off the "connected" LED.
    # The outdoor temperature and humidity are then written to the configuration file.
    def setOutdoorTemp(self, conf):
        print("kineticDisplay.setOutdoorTemp()")
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

    # This method is used to set the indoor temperature and humidity. It first turns on a (blue) LED,
    # then turns on the temperature sensor. It then attempts to read the temperature and humidity from the sensor.
    # If the sensor is not ready, it waits for one second and then tries again. This cycle repeats until the sensor
    # is ready. Once the sensor is ready, it reads the temperature and humidity and writes them to the configuration
    # file. Finally, it turns off the temperature sensor and the (blue) LED.
    def setIndoorTemp(self,conf):
        print("kineticDisplay.setIndoorTemp()")
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

    # This method is used to display the current time on the display. It first checks to see if the user has 
    # toggled the switch to 12 or 24 hour time. If 12 hour time is selected, it converts the hour to 12 hour 
    # time. If 24 hour time is selected, it leaves the hour as is. It then sends the current time to the digit 
    # controllers via UART.
    def displayTime(self, sync):
        print("kineticDisplay.displayTime()")
        self._colons.extend(True, True)     
        currentTime = "4{0}{1}{2:02}".format(uartCommandEnum.time, self.formatHour(sync.rtc.datetime()[4]), sync.rtc.datetime()[5])
        print("display time = {0}".format(currentTime[2:4]))
        self._sendDisplayUART(currentTime)
    
    # This method is used to display the current date. It sends a command via UART to the digit controllers to
    # display the date.
    def displayDate(self):
        print("kineticDisplay.displayDate()")   
        self._colons.retract(True, True)      
        dt = self._sync.rtc.datetime()
        print("dt = {0}".format(dt))  
        currentDate = "4{0}{1:02}{2:02}".format(uartCommandEnum.time, dt[1], dt[2])
        print("display date = {0}".format(currentDate))
        self._sendDisplayUART(currentDate)
    
    # This method is used to display the current temperature. The display of the indoor and outdoor temperatures 
    # alternate every other minute. It sends a command via UART to the digit controllers to display the indoor temperature. 
    # The following minute, it sends a command via UART to the digit controllers to display the outdoor temperature.
    def displayTemp(self,conf):
        print("kineticDisplay.displayTemp()")
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
            curTemp = "4{0}{1:02}AD".format(uartCommandEnum.time, int(t))
        else:
            curTemp = "4{0}{1:02}AC".format(uartCommandEnum.time, int(t))
        
        print("display temp = {0}".format(curTemp))
        self._sendDisplayUART(curTemp)
        
    # This method is used to display the current humidity. It first checks to see if the configuration is set 
    # to display the indoor or outdoor humidity. If the configuration allows the display of humidity, then it 
    # sends the current humidity to the digit controllers via UART.
    def displayHumidity(self, conf):
        print("kineticDisplay.displayHumidity()")
        displayIndoorTemp = conf.read("displayIndoorTemp")
        if displayIndoorTemp == 1:
            h = conf.read("humidreading")
            self._colons.extend(True, False)
            curHumid = "4{0}{1}AB".format(uartCommandEnum.time, h)
            print("display indoor humidity = {0}".format(curHumid))
            self._sendDisplayUART(curHumid)
            conf.write("displayIndoorTemp",0)
        else:
            self._colons.extend(False, True)
            h = conf.read("humidoutdoor")
            curHumid = "4{0}{1:02}AB".format(uartCommandEnum.time, h)
            print("display outdoor humidity = {0}".format(curHumid))
            self._sendDisplayUART(curHumid)
            conf.write("displayIndoorTemp",1)