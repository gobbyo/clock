from machine import UART, Pin
from servodisplay import servoDigitDisplay
import time
import config
import logs

#change this to hour_tens, hour_ones, minute_tens, or minute_ones
hour_tens = 0
hour_ones = 1
minute_tens = 2
minute_ones = 3

uartsignalpausetime = 1 #seconds

def decodeHex(value):
    returnval = value
    if value == "A":
        returnval = 10
    elif value == "B":
        returnval = 11
    elif value == "C":
        returnval = 12
    elif value == "D":
        returnval = 13
    elif value == "E":
        returnval = 14
    return int(returnval)

def validUART(value):
    if len(value) != 4:
        return False
    for d in value:
        i = decodeHex(d)
        if (i < 0) or (i > 14):
            return False
    return True

def updateDigit(digit,conf):
    prev = conf.read("previous")
    digit.setpreviousNumber(prev)

    i = conf.read("current")
    digit.paintNumber(i)
    print("Number {0}".format(i))

    conf.write("previous",i)

    i += 1
    if i >= len(digit._segnum):
        i = 0
    conf.write("current",i)

#picos must have common ground for uart to work
def main():
    log = logs.logger("receivetime.log",4096)
    log.write("main() called")
    prev = -1
    baudrate = [9600, 19200, 38400, 57600, 115200]
    

    conf = config.Config("digit.json")
    extend = conf.read("extend")
    retract = conf.read("retract")
    digitdisplay = conf.read("digit")
    log.write("read digit.json file")

    digit = servoDigitDisplay()
    digit.paintNumber(0x0E)

    for i in range(0,7):
        digit._extendAngles[i] = extend[i]
        digit._retractAngles[i] = retract[i]
    
    try:
        uart = UART(0, baudrate[0], rx=Pin(1))
        uart.init(baudrate[0], bits=8, parity=None, stop=1)
        log.write("baudrate = {0}".format(baudrate[0]))
        prev = -1
        
        while True:
            s = uart.any()
            log.write("uart.any() = {0}".format(s))

            if s > 0:
                b = bytearray('0000', 'utf-8')
                uart.readinto(b)

                if s == 4:
                    t = str(b.decode('utf-8'))
                    if validUART(t):
                        log.write("raw decode = {0}".format(t))
                        n = decodeHex(t[digitdisplay])
                        conf.write("current",n)
                        log.write("current = {0}, previous = {1}".format(n,prev))
                        if prev != n:
                            updateDigit(digit,conf)
                            prev = n
            time.sleep(uartsignalpausetime)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        digit.__del__()
        print('Done')
if __name__ == "__main__":
    main()
