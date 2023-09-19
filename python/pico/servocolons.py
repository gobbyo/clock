from machine import Pin
from servo import sg90
import time
import config

class servoColonsDisplay:
    _segpins = [2,3] # upper, lower
    _switchpins = [9,10] #upper, lower
    _ledpins = [16,17] #upper, lower
    _extendAngles = [20,20]
    _retractAngles = [90,90]
    _servospeed = 0.5 #default servo speed
    _servowait = 0.4
    _switches = []
    _servos = []    
    _leds = []
    _conf = None

    def __init__(self):
        #print("servoColonsDisplay constructor")
        for i in self._segpins:
            self._servos.append(sg90(i))
        for i in self._switchpins:
            self._switches.append(Pin(i, Pin.OUT))
        for i in range(0,len(self._ledpins)):
            self._leds.append(Pin(self._ledpins[i], Pin.OUT))
            self._leds[i].off()
        self._conf = config.Config("config.json")

    def __del__(self):
        self.paintNumber(0x0E)
        for led in self._leds:
            led.off()
        print("servoColonsDisplay destructor")

    def extend(self, upper, lower):
        colonstate = self._conf.read("colonstate")
        print("extend colons")
        for i in range(len(self._servos)):
            if ( i == 0 and upper == True) or (i == 1 and lower == True):
                if not colonstate[i]:
                    self._switches[i].on()
                    print("servo {0} move {1}".format(i,self._extendAngles[i]))
                    self._servos[i].move(self._extendAngles[i])
                    time.sleep(self._servowait)
                    self._switches[i].off()
                    self._leds[i].on()
                    colonstate[i] = True
        self._conf.write("colonstate",colonstate)

    def retract(self, upper, lower):
        colonstate = self._conf.read("colonstate")
        print("retract colons, colonstate={0}".format(colonstate))
        for i in range(len(self._servos)):
            if (i == 0 and upper == True) or (i == 1 and lower == True):
                if colonstate[i]:
                    self._leds[i].off()
                    self._switches[i].on() 
                    print("servo {0} move {1}".format(i,self._extendAngles[i]))
                    self._servos[i].move(self._retractAngles[i])
                    time.sleep(self._servowait)
                    self._switches[i].off()
                    colonstate[i] = False
        self._conf.write("colonstate",colonstate)