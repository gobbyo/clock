import machine
from machine import UART, Pin
from servodisplay import servoDigitDisplay
import time
import config
from digitconfigenum import uartCommandEnum
#import logs

uartsignalpausetime = 1 #second

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
    elif value == "F":
        returnval = 15
    return returnval

def validUART(value):
    print("validUART(len({0}))".format(len(value)))
    if len(value) != 6:
        return False
    for d in value:
        #print("validUART({0})".format(decodeHex(d)))
        try:
            i = int(decodeHex(d))
            if (i < 0) or (i > 15):
                print("validUART: invalid value {0}".format(i))
                return False
        except:
            print("validUART: invalid value {0}".format(i))
            return False
        finally:
            pass
    return True

def updateDigit(digit,conf,displaymotion):
    prev = conf.read("previous")
    digit.setpreviousNumber(prev)

    i = conf.read("current")
    if displaymotion == 0:
        digit.paintFastNumber(i)
    else:
        digit.paintSlowNumber(i)

    print("Number {0}".format(i))
    conf.write("previous",i)

    i += 1
    if i >= len(digit._segnum):
        i = 0
    conf.write("current",i)

#picos must have common ground for uart to work
def main():
    #log = logs.logger("receivetime.log",4096)
    #log.write("main() called")
    baudrate = [9600, 19200, 38400, 57600, 115200]
    
    conf = config.Config("digit.json")
    extend = conf.read("extend")
    retract = conf.read("retract")
    displaymotion = conf.read("motion")
    digitnumber = conf.read("digit")
    #log.write("read digit.json file")

    digit = servoDigitDisplay()
    digit.paintFastNumber(0x0E)

    for i in range(0,7):
        digit._extendAngles[i] = extend[i]
        digit._retractAngles[i] = retract[i]
    
    try:
        uart = UART(0, baudrate[0], rx=Pin(1))
        uart.init(baudrate[0], bits=8, parity=None, stop=1)
        #log.write("baudrate = {0}".format(baudrate[0]))

        prev = -1

        while True:
            time.sleep(uartsignalpausetime)
            if uart.any() > 0:
                b = bytearray('000000', 'utf-8')
                uart.readinto(b)
                d = str(b.decode('utf-8'))
                print("validUART({0}) = {1}".format(d,validUART(d)))
                if validUART(d):
                    print("Command = {0}".format(decodeHex(d[1])))
                    command = int(decodeHex(d[0]))
                    if (command == 4) or (command == digitnumber):
                        command = int(decodeHex(d[1]))
                        if (command == uartCommandEnum.time):
                            print("command to display current time for digit {0}".format(digitnumber))
                            n = int(decodeHex(d[digitnumber+2]))
                            if prev != n:
                                conf.write("current",n)
                                #log.write("current = {0}, previous = {1}".format(n,prev))
                                updateDigit(digit,conf,displaymotion)
                                prev = n
                        if (command == uartCommandEnum.extend): #extend angle
                            print("command to extend angles for digit {0} saved in config".format(digitnumber))
                            extend = conf.read("extend")
                            value = int(d[3:len(d)])
                            print("extend = {0}, extend[{1}] = {2}".format(extend, int(d[2]), value))
                            extend[int(d[2])] = value
                            digit._extendAngles[i] = extend
                            conf.write("extend",extend)
                        if (command == uartCommandEnum.retract): #retract angle
                            print("command to retract angle for digit {0} saved in config".format(digitnumber))
                            retract = conf.read("retract")
                            value = int(d[3:len(d)])
                            print("retract = {0}, retract[{1}] = {2}".format(retract, int(d[2]), value))
                            retract[int(d[2])] = value
                            digit._retractAngles[i] = retract
                            print("writing to config, retract = {0}".format(retract))
                            conf.write("retract",retract)
                        if (command == uartCommandEnum.motion):
                            print("writing to config, 'motion' = {0}".format(decodeHex(d[5])))
                            conf.write("motion",int(decodeHex(d[5])))
                        if (command == uartCommandEnum.current):
                            print("writing to config, 'current' = {0}".format(decodeHex(d[5])))
                            conf.write("current",int(decodeHex(d[5])))
                        if (command == uartCommandEnum.previous):
                            print("writing to config, 'previous' = {0}".format(decodeHex(d[5])))
                            conf.write("previous",int(decodeHex(d[5])))
                        if (command == decodeHex(uartCommandEnum.reset)):
                            print("reset")
                            machine.reset()
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        conf.write("current",0)
        conf.write("previous",14)
        digit.__del__()
        print('Done')
if __name__ == "__main__":
    main()
