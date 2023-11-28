#This file is to be uploaded as main.py for each digit 0-3

import machine
from machine import UART, Pin
from servodisplay import servoDigitDisplay
import time
import config
from digitconfigenum import uartCommandEnum
import uarttools
#import logs

waitTime = .1 #second

def updateDigit(digit,conf,displayMotion):
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

#TODO: move this to the servodisplay.py class
def rxextend(digit,command,conf,digitNumber):
    print("command to receive extend angles for digit {0} saved in config".format(digitNumber))
    digit._extendAngles = conf.read("extend")
    i = int(command[2])
    value = int(command[3:len(command)])
    digit._extendAngles[i] = value
    conf.write("extend",digit._extendAngles)
    digit.extend(i)

#TODO: move this to the servodisplay.py class
def rxretract(digit,command,conf,digitNumber):
    print("command to receive retract angles for digit {0} saved in config".format(digitNumber))
    digit._retractAngles = conf.read("retract")
    i = int(command[2])
    value = int(command[3:len(command)])
    digit._retractAngles[i] = value
    conf.write("retract",digit._retractAngles)
    digit.retract(i)

#TODO: move this to the servodisplay.py class
def txextend(digit,uart,digitNumber):
    print("send extend angles to controller for digit {0}".format(digitNumber))
    segment = 0
    for angle in digit._extendAngles:
        i = int(angle)
        b = bytearray('{0}{1}{2}{3:03}'.format(digitNumber, uartCommandEnum.txextend, segment,i), 'utf-8')
        uart.write(b)
        time.sleep(.1)
        segment += 1

#TODO: move this to the servodisplay.py class
def txretract(digit,uart,digitNumber):
    print("send retract angles to controller for digit {0}".format(digitNumber))
    segment = 0
    for angle in digit._retractAngles:
        i = int(angle)
        b = bytearray('{0}{1}{2}{3:03}'.format(digitNumber, uartCommandEnum.txretract, segment,i), 'utf-8')
        uart.write(b)
        time.sleep(.1)
        segment += 1

def main():
    conf = config.Config("digit.json")
    extend = conf.read("extend")
    retract = conf.read("retract")
    displayMotion = conf.read("motion")
    digitNumber = conf.read("digit")

    digit = servoDigitDisplay()
    digit.paintNumber(0x0E)

    for i in range(0,7):
        digit._extendAngles[i] = extend[i]
        digit._retractAngles[i] = retract[i]
    
    try:
        uart = UART(0, uarttools.baudRate[0], rx=Pin(uarttools.uartDigitRxPin), tx=Pin(uarttools.uartDigitTxPin), timeout=10)
        uart.init(uarttools.baudRate[0], bits=8, parity=None, stop=1)

        prev = -1

        while True:
            time.sleep(waitTime)
            if uart.any() > 0:
                b = bytearray('000000', 'utf-8')
                uart.readinto(b)
                d = str(b.decode('utf-8'))
                print("uarttools.validate({0}) = {1}".format(d,uarttools.validate(d)))
                if uarttools.validate(d):
                    print("Command = {0}".format(uarttools.decodeHex(d[1])))
                    command = int(uarttools.decodeHex(d[0]))
                    if (command == 4) or (command == digitNumber):
                        command = int(uarttools.decodeHex(d[1]))
                        if (command == uartCommandEnum.time):
                            print("command to display value for digit {0}".format(digitNumber))
                            n = int(uarttools.decodeHex(d[digitNumber+2]))
                            if prev != n:
                                conf.write("current",n)
                                updateDigit(digit,conf,displayMotion)
                                prev = n
                        if (command == uartCommandEnum.rxextend): #receive extend angle
                            rxextend(digit,d,conf,digitNumber)
                        if (command == uartCommandEnum.txextend): #send all extend angles
                            txextend(digit,uart,digitNumber)                        
                        if (command == uartCommandEnum.rxretract): #receive retract angle
                            rxretract(digit,d,conf,digitNumber)
                        if (command == uartCommandEnum.txretract): #send all retract angles
                            txretract(digit,uart,digitNumber)
                        if (command == uartCommandEnum.motion):
                            print("writing to config, 'motion' = {0}".format(uarttools.decodeHex(d[5])))
                            displayMotion = int(uarttools.decodeHex(d[5]))
                            conf.write("motion",displayMotion)
                        if (command == uartCommandEnum.current):
                            print("writing to config, 'current' = {0}".format(uarttools.decodeHex(d[5])))
                            conf.write("current",int(uarttools.decodeHex(d[5])))
                        if (command == uartCommandEnum.previous):
                            print("writing to config, 'previous' = {0}".format(uarttools.decodeHex(d[5])))
                            conf.write("previous",int(uarttools.decodeHex(d[5])))
                        if (command == uartCommandEnum.hybernate):
                            print("hybernate")
                            n = int(uarttools.decodeHex(d[digitNumber+2]))
                            machine.deepsleep(n * 1000)
                            machine.reset()
                        if (command == uartCommandEnum.timedhybernation):
                            print("timed hybernation")
                            n = int(d[2:6]) * 60
                            conf.write("timedhybernation", n)
                            machine.deepsleep(n * 1000)
                        if (command == uarttools.decodeHex(uartCommandEnum.reset)):
                            print("reset")
                            digit.paintNumber(0x0E)
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
