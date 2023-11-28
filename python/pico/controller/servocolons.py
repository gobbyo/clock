from machine import Pin
from servo import sg90
import config
import time

class servoColonsDisplay:
    _segpins = [2,3] # upper, lower
    _switchpins = [9,10] #upper, lower
    _ledpins = [16,17] #upper, lower
    _extendAngles = [20,20]
    _retractAngles = [110,110]
    _rateofmovement = 3 #degrees
    _servospeed = 0.03 #default servo speed
    _servowait = 0.4
    _switches = []
    _servos = []    
    _leds = []
    _config = None

    def __init__(self, conf):
        print("servoColonsDisplay constructor")
        self._config = conf
        colonstate = self._config.read("colonstate")

        for i in self._segpins:
            self._servos.append(sg90(i))
        for i in self._switchpins:
            self._switches.append(Pin(i, Pin.OUT))
        for i in range(0,len(self._ledpins)):
            self._leds.append(Pin(self._ledpins[i], Pin.OUT))
            if colonstate[i]:
                self._leds[i].on()
            else:
                self._leds[i].off()

    def __del__(self):
        for led in self._leds:
            led.off()
        for i in range(0, 2):
            self._servos[i].move(self._retractAngles[i])
            print("servo {0} move {1}".format(i,self._retractAngles[i]))
            i += 1
        print("servoColonsDisplay destructor")

    def extend(self, upper, lower):
        colonstate = self._config.read("colonstate")
        print("extend colons, colonstate={0}".format(colonstate))
        for i in range(0,2):
            if ( i == 0 and upper == True) or (i == 1 and lower == True):
                if not colonstate[i]:
                    self._switches[i].on()
                    print("extend {0} move {1}".format(i,self._extendAngles[i]))
                    self._servos[i].move(self._extendAngles[i])
                    time.sleep(self._servowait)
                    self._switches[i].off()
                    self._leds[i].on() # turns on AFTER the servo extends the segment
                    colonstate[i] = True
        self._config.write("colonstate",colonstate)

    def retract(self, upper, lower):
        colonstate = self._config.read("colonstate")
        print("retract colons, colonstate={0}".format(colonstate))
        for i in range(0,2):
            if (i == 0 and upper == True) or (i == 1 and lower == True):
                if colonstate[i]:
                    self._leds[i].off() # turns off BEFORE the servo retracts the segment
                    self._switches[i].on() 
                    print("retract {0} move {1}".format(i,self._retractAngles[i]))
                    self._servos[i].move(self._retractAngles[i])
                    time.sleep(self._servowait)
                    self._switches[i].off()
                    colonstate[i] = False
        self._config.write("colonstate",colonstate)