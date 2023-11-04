import machine
from digitconfigenum import uartCommandEnum
import config
import time

def rxextend(command,conf,digitNumber):
    print("command to receive extend angles for digit {0} saved in config".format(digitNumber))
    extend = conf.read("extend")
    i = int(command[2])
    value = int(command[3:len(command)])
    print("extend = {0}, extend[{1}] = {2}".format(extend, i, value))
    extend[i] = value
    conf.write("extend",extend)

def rxretract(command,conf,digitNumber):
    print("command to receive retract angles for digit {0} saved in config".format(digitNumber))
    retract = conf.read("retract")
    i = int(command[2])
    value = int(command[3:len(command)])
    print("retract = {0}, retract[{1}] = {2}".format(retract, i, value))
    retract[i] = value
    #digit._retractAngles[i] = retract
    print("writing to config, retract = {0}".format(retract))
    conf.write("retract",retract)

def txextend(conf,uart,digitNumber):
    print("send extend angles to controller for digit {0}".format(digitNumber))
    extend = conf.read("extend")
    segment = 0
    for angle in extend:
        i = int(angle)
        b = bytearray('{0}{1}{2}{3:03}'.format(digitNumber, uartCommandEnum.txextend, segment,i), 'utf-8')
        uart.write(b)
        time.sleep(.1)
        segment += 1

def txretract(conf,uart,digitNumber):
    print("send retract angles to controller for digit {0}".format(digitNumber))
    retract = conf.read("retract")
    segment = 0
    for angle in retract:
        i = int(angle)
        b = bytearray('{0}{1}{2}{3:03}'.format(digitNumber, uartCommandEnum.txretract, segment,i), 'utf-8')
        uart.write(b)
        time.sleep(.1)
        segment += 1

rxpin = const(1)
txpin = const(0)
#picos must have common ground for uart to work
def main():
    baudrate = [9600, 19200, 38400, 57600, 115200]
    conf = config.Config("digit.json")
    
    try:
        uart = machine.UART(0, baudrate[0], tx=machine.Pin(txpin), rx=machine.Pin(rxpin))
        uart.init(baudrate[0], bits=8, parity=None, stop=1)
        countreset = 50
        while True:
            if countreset > 50:
                countreset = 0
            else:
                countreset += 1

            if countreset % 11 == 0:
                txretract(conf,uart,0)
            
            if countreset % 41 == 0:
                txextend(conf,uart,0)
            
            if uart.any():
                b = bytearray('000000', 'utf-8')
                uart.readinto(b)
                t = b.decode('utf-8')
                print(t)    
            time.sleep(.1)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        print('Done')

if __name__ == "__main__":
    main()
