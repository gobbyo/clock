import machine
from machine import UART, Pin
from servodisplay import servoDigitDisplay
import time
import config
from digitconfigenum import uartCommandEnum
#import logs

waitTime = .25 #second

def decodeHex(value):
    returnVal = value
    if value == "A":
        returnVal = 10
    elif value == "B":
        returnVal = 11
    elif value == "C":
        returnVal = 12
    elif value == "D":
        returnVal = 13
    elif value == "E":
        returnVal = 14
    elif value == "F":
        returnVal = 15
    return returnVal

def validate(value):
    print("validate(len({0}))".format(len(value)))
    if len(value) != 6:
        return False
    for d in value:
        #print("validate({0})".format(decodeHex(d)))
        try:
            i = int(decodeHex(d))
            if (i < 0) or (i > 15):
                print("validate: invalid value {0}".format(i))
                return False
        except:
            print("validate: invalid value {0}".format(value))
            return False
        finally:
            pass
    return True

def updateDigit(digit,conf,displayMotion):
    prev = conf.read("previous")
    digit.setpreviousNumber(prev)

    i = conf.read("current")
    if displayMotion == 0:
        digit.paintFastNumber(i)
    else:
        digit.paintSlowNumber(i)

    print("Number {0}".format(i))
    conf.write("previous",i)

    i += 1
    if i >= len(digit._segnum):
        i = 0
    conf.write("current",i)

def main():
    baudRate = [9600, 19200, 38400, 57600, 115200]
    
    conf = config.Config("digit.json")
    extend = conf.read("extend")
    retract = conf.read("retract")
    displayMotion = conf.read("motion")
    digitNumber = conf.read("digit")

    digit = servoDigitDisplay()
    digit.paintFastNumber(0x0E)

    for i in range(0,7):
        digit._extendAngles[i] = extend[i]
        digit._retractAngles[i] = retract[i]
    
    try:
        uart = UART(0, baudRate[0], rx=Pin(1))
        uart.init(baudRate[0], bits=8, parity=None, stop=1)

        prev = -1

        while True:
            time.sleep(waitTime)
            if uart.any() > 0:
                b = bytearray('000000', 'utf-8')
                uart.readinto(b)
                d = str(b.decode('utf-8'))
                print("validate({0}) = {1}".format(d,validate(d)))
                if validate(d):
                    print("Command = {0}".format(decodeHex(d[1])))
                    command = int(decodeHex(d[0]))
                    if (command == 4) or (command == digitNumber):
                        command = int(decodeHex(d[1]))
                        if (command == uartCommandEnum.time):
                            print("command to display value for digit {0}".format(digitNumber))
                            n = int(decodeHex(d[digitNumber+2]))
                            if prev != n:
                                conf.write("current",n)
                                updateDigit(digit,conf,displayMotion)
                                prev = n
                        if (command == uartCommandEnum.extend): #extend angle
                            print("command to extend angles for digit {0} saved in config".format(digitNumber))
                            extend = conf.read("extend")
                            i = int(d[2])
                            value = int(d[3:len(d)])
                            print("extend = {0}, extend[{1}] = {2}".format(extend, i, value))
                            extend[i] = value
                            digit._extendAngles[i] = extend
                            conf.write("extend",extend)
                        if (command == uartCommandEnum.retract): #retract angle
                            print("command to retract angle for digit {0} saved in config".format(digitNumber))
                            retract = conf.read("retract")
                            i = int(d[2])
                            value = int(d[3:len(d)])
                            print("retract = {0}, retract[{1}] = {2}".format(retract, i, value))
                            retract[i] = value
                            digit._retractAngles[i] = retract
                            print("writing to config, retract = {0}".format(retract))
                            conf.write("retract",retract)
                        if (command == uartCommandEnum.motion):
                            print("writing to config, 'motion' = {0}".format(decodeHex(d[5])))
                            displayMotion = int(decodeHex(d[5]))
                            conf.write("motion",displayMotion)
                        if (command == uartCommandEnum.current):
                            print("writing to config, 'current' = {0}".format(decodeHex(d[5])))
                            conf.write("current",int(decodeHex(d[5])))
                        if (command == uartCommandEnum.previous):
                            print("writing to config, 'previous' = {0}".format(decodeHex(d[5])))
                            conf.write("previous",int(decodeHex(d[5])))
                        if (command == uartCommandEnum.hybernate):
                            print("hybernate")
                            n = int(decodeHex(d[digitNumber+2]))
                            machine.deepsleep(n * 1000)
                            machine.reset()
                        if (command == uartCommandEnum.timedhybernation):
                            print("timed hybernation")
                            i = len(d)
                            while i > 0 and d[i-1] == "F":
                                i -= 1
                            n = int(int(d[3:i])) * 60
                            conf.write("timed hybernation for {0} minute(s)", n)
                            machine.deepsleep(n * 1000)
                        if (command == decodeHex(uartCommandEnum.reset)):
                            print("reset")
                            digit.paintFastNumber(0x0E)
                            conf.write("current",0)
                            conf.write("previous",14)
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
