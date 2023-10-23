from machine import Pin, UART
from uarttools import decodeHex, validate
import time

#   4 digit 7 segmented LED
#
#       digit 1        digit 2        digit 3        digit 4
#        _a_            _a_            _a_            _a_
#     f |_g_| b      f |_g_| b      f |_g_| b      f |_g_| b
#     e |___| c _h   e |___| c _h   e |___| c _h   e |___| c _h
#         d              d              d              d
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
# A =   0110 0011   0x63  #degrees
# B =   0101 1100   0x5C  #percent
# C =   0011 1001   0x39  #celcius
# D =   0111 0001   0x71  #farhenheit
# E =   0111 1001   0x79  #clear
# F =   0111 0001   0x71  #ignore
segnum = [0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x67,0x63,0x5C,0x39,0x71,0x79,0x71]

waitreps = 50
waitonpaint = 0.001
# The variable below can be any number of digits for a 7 segment display. 
# For example, a 2 digit 7 segment display is digitpins=[1,0], four digit 7 segment display is digitpins=[3,2,1,0], etc.
fourdigitpins = [3,2,1,0]
#segnum = [0x3F,0x06,0x5B,0x4F,0x66,0x6D,0x7D,0x07,0x7F,0x67]
fourlatchpin = const(7) #RCLK
fourclockpin = const(6) #SRCLK
fourdatapin = const(8) #SER

twodigitpins = [21,16]
twoclockpin = const(27) #SRCLK
twodatapin = const(28) #SER
twolatchpin = const(26) #RCLK

class segdisplays:
    def __init__(self):
        self.twodigits = []
        for d in twodigitpins:
            pin = Pin(d, Pin.OUT)
            pin.high()
            self.twodigits.append(pin)
        self. fourdigits = []

        for d in fourdigitpins:
            pin = Pin(d, Pin.OUT)
            pin.high()
            self.fourdigits.append(pin)
    def __del__(self):
        for t in self.twodigits:
            self.set_register(0,twolatch,twoclock,twodata)
            t.low()
        for f in self.fourdigits:
            self.set_register(0,fourlatch,fourclock,fourdata)
            f.low()

    def getArray(self,val):
        a = [0,0,0,0,0,0,0,0]
        i = 0
        for s in a:
            a[i] = (val & (0x01 << i)) >> i
            i += 1
        return a

    def set_register(self,val,latch,clock,data):
        input = [0,0,0,0,0,0,0,0]
        #open latch for data
        clock.low()
        latch.low()
        clock.high()

        input = self.getArray(val)

        #load data in register
        for i in range(7, -1, -1):
            clock.low()
            if input[i] == 1:
                data.high()
            else:
                data.low()
            clock.high()

        #close latch for data
        clock.low()
        latch.high()
        clock.high()

    def paintdigit(self,val,digit,latch,clock,data):
        digit.low()
        #display the value
        self.set_register(val,latch,clock,data)
        #wait to see it
        time.sleep(waitonpaint)
        #clear the display
        self.set_register(0,latch,clock,data)
        digit.high()

    def printnum(self,d,digits,latch,clock,data):
        for i in range(0,2):
            h = int(decodeHex(d[i]))
            val = segnum[int(h)]
            self.paintdigit(val,digits[i],latch,clock,data)

    def printfloat(self,f,digits,latch,clock,data):
        for i in range(0,4):
            h = int(decodeHex(f[i]))
            val = segnum[int(h)]
            self.paintdigit(val,digits[i],latch,clock,data)

def main():
    uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(13))
    uart.init(9600, bits=8, parity=None, stop=1)
    print("UART is configured as : ", uart)
    fourlatch = Pin(fourlatchpin, Pin.OUT)
    fourclock = Pin(fourclockpin, Pin.OUT)
    fourdata = Pin(fourdatapin, Pin.OUT)
        
    twolatch = Pin(twolatchpin, Pin.OUT)
    twoclock = Pin(twoclockpin, Pin.OUT)
    twodata = Pin(twodatapin, Pin.OUT)
    
    segdisp = segdisplays()

    try:
        print("circuit test...")

        for d in segdisp.twodigits:
            for i in range(8):
                for w in range(waitreps):
                    val = 0x01 << i
                    segdisp.paintdigit(val,d,twolatch,twoclock,twodata)
        
        for d in segdisp.fourdigits:
            for i in range(8):
                for w in range(waitreps):
                    val = 0x01 << i
                    segdisp.paintdigit(val,d,fourlatch,fourclock,fourdata)

        print("display test...")
        prev = d = '000000'
        while True:
            if uart.any() > 0:
                b = bytearray('000000', 'utf-8')
                uart.readinto(b)
                d = str(b.decode('utf-8'))
            if validate(d):
                if prev == d:
                    for w in range(waitreps):
                        segdisp.printnum(d[0:2],segdisp.twodigits,twolatch,twoclock,twodata)
                        segdisp.printfloat(d[2:6],segdisp.fourdigits,fourlatch,fourclock,fourdata)
                else:
                    prev = d
    finally:
        print("test finished")

if __name__ == '__main__':
	main()