from machine import Pin
from servo import sg90
import time

class servoDigitDisplay:
    _segpins = [2,3,6,7,8,9,10] # a,b,c,d,e,f,g
    _switchpins = [11,12,13,14,15,16,17]
    _ledpins = [18,19,20,21,22,26,27]
    _extendAngles = [0,0,0,0,0,0,0]
    _retractAngles = [90,90,90,90,90,90,90]
    _servospeed = 0.05 #default servo speed
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
    segnum = [0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x67]
    servos = []
    switches = []
    leds = []
    clearRegister = [0,0,0,0,0,0,0,0]
    previousNumber = clearRegister

    def __init__(self):
        #print("servoDigitDisplay constructor")
        for i in self._segpins:
            self.servos.append(sg90(i))
        for i in self._switchpins:
            self.switches.append(Pin(i, Pin.OUT))
        for i in range(0,len(self._ledpins)):
            self.leds.append(Pin(self._ledpins[i], Pin.OUT))
            self.leds[i].off()

    def __del__(self):
        self.clearDisplay()
        for led in self.leds:
            led.off()
        print("servoDigitDisplay destructor")

    def extend(self,index):
        #print("extend {0}".format(index))
        i = self._retractAngles[index]
        self.switches[index].on()

        #while i >= self._extendAngles[index]:
            #print("angle = {0}".format(i))
        #    self.servos[index].move(i)
        #    time.sleep(self._servospeed)
        #    i -= 5
        
        self.servos[index].move(self._extendAngles[index])
        time.sleep(.2)
        self.switches[index].off()
        self.leds[index].on()

    def retract(self,index):
        #print("retract {0}".format(index))
        self.leds[index].off()
        i = self._extendAngles[index]
        self.switches[index].on()
        #while i <= self._retractAngles[index]:
            #print("angle = {0}".format(i))
        #    self.servos[index].move(i)
        #    time.sleep(self._servospeed)
        #    i += 5
        
        self.servos[index].move(self._retractAngles[index])
        time.sleep(.2)
        self.switches[index].off()

    def getArray(self,val):
        a = [0,0,0,0,0,0,0,0]
        i = 0
        for s in a:
            a[i] = (val & (0x01 << i)) >> i
            i += 1
        return a

    def clearDisplay(self):
        for i in range(0,7):
            if self.previousNumber[i] == 1:
                self.retract(i)
                time.sleep(self._servospeed)
        self.previousNumber = self.clearRegister
    
    def paintNumber(self,val):
        input = []
        input = self.getArray(self.segnum[val])

        for i in range(0,len(input)):
            if input[i] == 1:
                if self.previousNumber[i] == 0:
                    self.extend(i)               
            if input[i] == 0:
                if self.previousNumber[i] == 1:
                    self.retract(i)
            time.sleep(self._servospeed)
            
        self.previousNumber = input
    
    def testServos(self):
        print("testServos")
        self.clearDisplay()
        seg_sequence = [0,1,6,4,3,2,6,5,0]
        i = 0
        self.extend(seg_sequence[i])
        while i in seg_sequence:
            if i < len(seg_sequence):
                self.extend(seg_sequence[i+1])        
                print("extend {0}".format(i))
            self.retract(seg_sequence[i])
            print("retract {0}".format(i))
            i += 1
        self.retract(seg_sequence[i])
        self.clearDisplay()