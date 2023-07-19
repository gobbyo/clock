from machine import Pin, PWM
from servo import sg90
import time

class servoDigitDisplay:
    segpins = [3,5,6,7,8,9,10] # a,b,c,d,e,f,g
    switchpins = [11,12,13,14,15,16,17] # a,b,c,d,e,f,g
    ledpins = [18,19,20,21,22,26,27] # a,b,c,d,e,f,g
    extendAngles = [0,0,0,0,0,0,0]
    retractAngles = [90,90,90,90,90,90,90]
    servospeed = 0.05 #default servo speed
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
    switch = []
    clearRegister = [0,0,0,0,0,0,0,0]
    previousNumber = clearRegister

    def __init__(self):
        #print("servoDigitDisplay constructor")
        for i in self.segpins:
            self.servos.append(sg90(i))
        for i in self.switchpins:
            self.switch.append(Pin(i, Pin.OUT))

    def __del__(self):
        self.clearDisplay()
        print("servoDigitDisplay destructor")

    def switchOn(self,index):
        self.switch[index].on()

    def switchOff(self,index):
        self.switch[index].off()

    def extend(self,index):
        #print("extend {0}".format(index))
        i = self.retractAngles[index]
        self.switchOn(index)
        
        while i >= self.extendAngles[index]:
            #print("angle = {0}".format(i))
            self.servos[index].move(i)
            time.sleep(self.servospeed)
            i -= 5
        
        #needed when the servo speed is too fast
        self.servos[index].move(self.extendAngles[index])
        time.sleep(.2)
        self.switchOff(index)

    def retract(self,index):
        #print("retract {0}".format(index))
        i = self.extendAngles[index]
        self.switchOn(index)
        while i <= self.retractAngles[index]:
            #print("angle = {0}".format(i))
            self.servos[index].move(i)
            time.sleep(self.servospeed)
            i += 5
        
        #needed when the servo speed is too fast
        self.servos[index].move(self.retractAngles[index])
        time.sleep(.2)
        self.switchOff(index)

    def getArray(self,val):
        a = [0,0,0,0,0,0,0,0]
        i = 0
        for s in a:
            a[i] = (val & (0x01 << i)) >> i
            i += 1
        #print("getArray {0}".format(a))
        return a

    def clearDisplay(self):
        for i in range(0,8):
            if self.previousNumber[i] == 1:
                self.retract(i)
    
    def paintNumber(self,val):
        input = []
        input = self.getArray(self.segnum[val])

        #print("paintNumber {0}".format(input))
        #print("previousNumber {0}".format(self.previousNumber))

        for i in range(0,len(input)):
            if input[i] == 1:
                if self.previousNumber[i] == 0:
                    self.extend(i)               
            if input[i] == 0:
                if self.previousNumber[i] == 1:
                    self.retract(i)
        
        self.previousNumber = input