import config
from digitconfigenum import uartCommandEnum
import time
import machine

uartTxPin = const(12)
uartRxPin = const(13)

def changeAnglesUART(digit, commandtype, uart, angles):
    if commandtype == uartCommandEnum.extend:
        print('extend:')
    else:
        print('retract:')
    i = 0
    for e in angles:
        command = str(digit) + str(commandtype) + str(i) + 'FFF'
        strExtend = str(e)
        command = command[0:6-len(strExtend)] + str(e)
        print('   {0}'.format(command))   
        i += 1 
        b = bytearray(command, 'utf-8')
        uart.write(b)
        time.sleep(.1)

def main():
    digit = 3
    baudRate = [9600, 19200, 38400, 57600, 115200]
    uart = machine.UART(0, baudRate[0], tx=machine.Pin(uartTxPin), rx=machine.Pin(uartRxPin))
    uart.init(baudRate[0], bits=8, parity=None, stop=1)

    extend = [20, 10, 20, 10, 10, 10, 20]
    retract = [100, 105, 100, 100, 100, 100, 110]
    

    
    try:
        changeAnglesUART(digit, uartCommandEnum.extend, uart, extend)
        changeAnglesUART(digit, uartCommandEnum.retract, uart, retract)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        print('Done')

if __name__ == '__main__':
    main()