from machine import Pin
from servo import sg90
import time

class servoDigitDisplay:
    _segpins = [2,3,4,5,6,7,8] # a,b,c,d,e,f,g
    _switchpins = [9,10,11,12,13,14,15]
    _ledpins = [16,17,18,19,20,21,22]
    _extendAngles = [0,0,0,0,0,0,0]
    _retractAngles = [90,90,90,90,90,90,90]
    _servospeed = 0.2 #default servo speed
    _servowait = 0.4
    # 0 = 	0011 1111   0x3F
    # 1 =	0000 0110   0x06
    # 2 =	0101 1011   0x5B
    # 3 =	0100 1111   0x4F
    # 4 =	0110 0110   0x66
    # 5 =	0110 1101   0x6D
    # 6 =	0111 1101   0x7D
    # 7 =	0000 0111   0x07
    # 8 =   0111 1111   0x7F
    # 9 =   0110 0111   0x67
    # A =   0110 0011   0x63  #degrees
    # B =   0101 1100   0x5C  #percent
    # C =   0011 1001   0x39  #celcius
    # D =   0111 0001   0x71  #farhenheit
    # E =   0000 0000   0x00  #clear
    _segnum = [0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x67,0x63,0x5C,0x39,0x71,0x00]
    _switches = []
    _servos = []    
    _leds = []
    _clearRegister = [0,0,0,0,0,0,0,0]
    _previousNumber = _clearRegister

    def __init__(self):
        #print("servoDigitDisplay constructor")
        for i in self._segpins:
            self._servos.append(sg90(i))
        for i in self._switchpins:
            self._switches.append(Pin(i, Pin.OUT))
        for i in range(0,len(self._ledpins)):
            self._leds.append(Pin(self._ledpins[i], Pin.OUT))
            self._leds[i].off()

    def __del__(self):
        self.paintNumber(0x0E)
        for led in self._leds:
            led.off()
        print("servoDigitDisplay destructor")
    
    def setpreviousNumber(self,val):
        self._previousNumber = self.getArray(self._segnum[val])
        for i in range(0,len(self._previousNumber)):
            if self._previousNumber[i] == 1:
                self._leds[i].on()
    
    def getArray(self,val):
        a = [0,0,0,0,0,0,0,0]
        i = 0
        for s in a:
            a[i] = (val & (0x01 << i)) >> i
            i += 1
        return a

    def paintNumber(self,val):
        current = []
        current = self.getArray(self._segnum[val])
        result = [-1,-1,-1,-1,-1,-1,-1]

        for i in range(0,len(current)):
            t = self._previousNumber[i] + current[i]
            if not (t == 0 or t == 2):
                result[i] = current[i]

        extendAngles = self._extendAngles.copy()
        retractAngles = self._retractAngles.copy()

        #Start change of digit, turn on power for servos, turn off LEDs
        for i in range(0,len(result)):
            if result[i] == 1:
                print("extend start {0}".format(i))
                self._switches[i].on()
                self._leds[i].off()
            if result[i] == 0:
                print("retract start {0}".format(i))
                self._switches[i].on()
                self._leds[i].off()

        #Move segments to change digit
        speedofmovement = 5 #degrees
        end = round(90/speedofmovement)

        for e in range(end):
            print("e={0} of end={1}".format(e,end))
            for i in range(len(result)):
                if result[i] == 1:
                    retractAngles[i] -= speedofmovement
                    if retractAngles[i] >= self._extendAngles[i]:
                        print("{0} extend angle = {1}".format(i, retractAngles[i]))
                        self._servos[i].move(retractAngles[i])
                    #time.sleep(.2)
                if result[i] == 0:
                    extendAngles[i] += speedofmovement
                    if extendAngles[i] <= self._retractAngles[i]:
                        print("{0} retract angle = {1}".format(i, extendAngles[i]))
                        self._servos[i].move(extendAngles[i])
            time.sleep(.2)

        #Finish moving segments, turn off power to servos, turn on LEDs
        for i in range(len(result)):
            if result[i] == 1:
                print("extend complete {0}".format(i))
                self._servos[i].move(extendAngles[i]) #finish any leftover
                self._switches[i].off()
                self._leds[i].on()
            if result[i] == 0:
                print("retract complete {0}".format(i))
                self._servos[i].move(retractAngles[i]) #finish any leftover
                self._switches[i].off()
                self._leds[i].off()
        self._previousNumber = current