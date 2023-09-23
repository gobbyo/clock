from machine import Pin
from servo import sg90
import time

class servoColonsDisplay:
    _segpins = [2,3] # upper, lower
    _switchpins = [9,10] #upper, lower
    _ledpins = [16,17] #upper, lower
    _extendAngles = [20,20]
    _retractAngles = [90,90]
    _rateofmovement = 3 #degrees
    _servospeed = 0.03 #default servo speed
    _servowait = 0.4
    _switches = []
    _servos = []    
    _leds = []
    _conf = None

    def __init__(self, conf):
        #print("servoColonsDisplay constructor")
        self._conf = conf
        for i in self._segpins:
            self._servos.append(sg90(i))
        for i in self._switchpins:
            self._switches.append(Pin(i, Pin.OUT))
        for i in range(0,len(self._ledpins)):
            self._leds.append(Pin(self._ledpins[i], Pin.OUT))
            self._leds[i].off()
        #self._conf = config.Config("config.json")

    def __del__(self):
        self.paintNumber(0x0E)
        for led in self._leds:
            led.off()
        #print("servoColonsDisplay destructor")

    def extend(self, upper, lower):
        colonstate = self._conf.read("colonstate")
        #print("extend colons")
        for i in range(len(self._servos)):
            if ( i == 0 and upper == True) or (i == 1 and lower == True):
                if not colonstate[i]:
                    self._switches[i].on()
                    #print("servo {0} move {1}".format(i,self._extendAngles[i]))
                    self._servos[i].move(self._extendAngles[i])
                    time.sleep(self._servowait)
                    self._switches[i].off()
                    self._leds[i].on()
                    colonstate[i] = True
        self._conf.write("colonstate",colonstate)

    def retract(self, upper, lower):
        colonstate = self._conf.read("colonstate")
        #print("retract colons, colonstate={0}".format(colonstate))
        for i in range(len(self._servos)):
            if (i == 0 and upper == True) or (i == 1 and lower == True):
                if colonstate[i]:
                    self._leds[i].off()
                    self._switches[i].on() 
                    #print("servo {0} move {1}".format(i,self._extendAngles[i]))
                    self._servos[i].move(self._retractAngles[i])
                    time.sleep(self._servowait)
                    self._switches[i].off()
                    colonstate[i] = False
        self._conf.write("colonstate",colonstate)
    
    def paintFastNumber(self, direction, upper, lower):
        input = []
        input = self.getArray(self._segnum[val])
        print("paintNumber._previousNumber {0}".format(self._previousNumber))

        if direction == 1:
            self.extend(upper, lower)           
        else:
            self.retract(upper, lower)

        self._previousNumber = input

    #todo: add support for colons in slow motion
    def paintSlowNumber(self, direction, upper, lower):
        current = []
        current = self.getArray(self._segnum[val])
        colonstate = self._conf.read("colonstate")
        result = [-1,-1]
        for i in range(0,len(current)):
            t = self._previousNumber[i] + current[i]
            if not (t == 0 or t == 2):
                result[i] = current[i]

        extendAngles = self._extendAngles.copy()
        retractAngles = self._retractAngles.copy()

        #Start change of digit, turn on power for servos, turn off LEDs
        for i in range(0,len(result)):
            if (i == 0 and upper == True) or (i == 1 and lower == True):
                if colonstate[i] == True:
                    #print("extend start {0}".format(i))
                    self._switches[i].on()
                    self._leds[i].off()
                if colonstate[i] == False:
                    #print("retract start {0}".format(i))
                    self._switches[i].on()
                    self._leds[i].off()

        #Move segments to change digit
        end = round(90/self._rateofmovement)

        for e in range(end):
            #print("e={0} of end={1}".format(e,end))
            for i in range(len(result)):
                if (i == 0 and upper == True) or (i == 1 and lower == True):
                    if colonstate[i] == True:
                        retractAngles[i] -= self._rateofmovement
                        if retractAngles[i] >= self._extendAngles[i]:
                            #print("{0} extend angle = {1}".format(i, retractAngles[i]))
                            self._servos[i].move(retractAngles[i])
                    if colonstate[i] == False:
                        extendAngles[i] += self._rateofmovement
                        if extendAngles[i] <= self._retractAngles[i]:
                            #print("{0} retract angle = {1}".format(i, extendAngles[i]))
                            self._servos[i].move(extendAngles[i])
            time.sleep(self._servospeed)

        #Finish moving segments, turn off power to servos, turn on LEDs
        for i in range(len(result)):
            if (i == 0 and upper == True) or (i == 1 and lower == True):
                if result[i] == 1:
                    #print("extend complete {0}".format(i))
                    self._servos[i].move(extendAngles[i]) #finish any leftover
                    time.sleep(.3)
                    self._switches[i].off()

                if result[i] == 0:
                    #print("retract complete {0}".format(i))
                    self._servos[i].move(retractAngles[i]) #finish any leftover
                    time.sleep(.3)
                    self._switches[i].off()
        
        for i in range(len(result)):
            if result[i] == 1:
                self._leds[i].on()
            if result[i] == 0:
                self._leds[i].off()
        self._previousNumber = current