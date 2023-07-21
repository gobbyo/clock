from machine import Pin
import time

#   4 digit 7 segmented LED
#
#       digit 1        digit 2        digit 3        digit 4
#        _a_            _a_            _a_            _a_
#     f |_g_| b      f |_g_| b      f |_g_| b      f |_g_| b
#     e |___| c _h   e |___| c _h   e |___| c _h   e |___| c _h
#         d              d              d              d
#
# num   hgfe dcba   hex
#
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

class digitdisplay:
    waitreps = 400
    waitonpaint = 0.001
    # The variable below can be any number of digits for a 7 segment display. 
    # For example, a 2 digit 7 segment display is digitpins=[1,0], four digit 7 segment display is digitpins=[3,2,1,0], etc.
    segnum = [0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x67]

    def __init__(self):
        self.digitpins = [3,2,1,0]
        self.latchpin = 7
        self.clockpin = 6
        self.datapin = 8
        self.digits = []
        #self.setPins(self.digitpins,self.latchpin,self.clockpin,self.datapin)

    def setPins(self,Digitpins,Latchpin,Clockpin,Datapin):
        self.digitpins = Digitpins
        self.clockpin = Clockpin
        self.latchpin = Latchpin
        self.datapin = Datapin

        self.latch = Pin(self.latchpin, Pin.OUT)
        self.clock = Pin(self.clockpin, Pin.OUT)
        self.data = Pin(self.datapin, Pin.OUT)

        i = 0
        while i < len(self.digitpins):
            self.digits.append(Pin(self.digitpins[i], Pin.OUT))
            print("digit pin {0}".format(self.digitpins[i]))
            self.digits[i].high()
            i += 1
        
    def __del__(self):
        for d in self.digits:
            self.setregister(0)
            d.low()

    def getArray(self,val):
        a = [0,0,0,0,0,0,0,0]
        i = 0
        for s in a:
            a[i] = (val & (0x01 << i)) >> i
            i += 1
        return a

    def setregister(self,val):
        input = [0,0,0,0,0,0,0,0]
        #open latch for data
        self.clock.low()
        self.latch.low()
        self.clock.high()

        input = self.getArray(val)

        #load data in register
        for i in range(7, -1, -1):
            self.clock.low()
            if input[i] == 1:
                self.data.high()
            else:
                self.data.low()
            self.clock.high()

        #close latch for data
        self.clock.low()
        self.latch.high()
        self.clock.high()

    def paintdigit(self,val,digit):
        digit.low()
        #display the value
        self.setregister(val)
        #wait to see it
        time.sleep(self.waitonpaint)
        #clear the display
        self.setregister(0)
        digit.high()

    def printnum(self,num):
        reps = self.waitreps/(len(digits)*self.waitonpaint*1000)
        for w in range(reps):
            d = len(digits)-1
            i = len(num)-1
            while i >= 0 & d >= 0:
                if(num[i].isdigit()):
                    val = segnum[int(num[i])]
                    self.paintdigit(val,digits[d],latch,clock,data)
                    d -= 1
                i -= 1

    def printfloat(self,f):
        reps = self.waitreps/(len(self.digits)*self.waitonpaint*1000)
        for w in range(reps):
            if f < 100: 
                num = "{:.2f}".format(f)

                i = len(num)-1
                decimal = False
                d = 3
                while i >= 0 & d >= 0:
                    if(num[i].isdigit()):
                        val = self.segnum[int(num[i])]
                        if decimal:
                            val |= 0x01 << 7
                            decimal = False
                        self.paintdigit(val,self.digits[d])
                        d -= 1
                    else:
                        decimal = True
                    i -= 1

def main():
    display = digitdisplay()
    display.setPins([3,2,1,0],7,6,8)

    try:
        i = 1
        while i <= 20:
            display.printfloat(i)
            i += 1.125
    finally:
        display.__del__()

if __name__ == '__main__':
	main()