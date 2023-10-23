from machine import UART, Pin
import time

rxpin = const(13)
#picos must have common ground for uart to work
def main():
    baudrate = [9600, 19200, 38400, 57600, 115200]
    
    try:
        uart = UART(0, baudrate[0], rx=Pin(rxpin))
        uart.init(baudrate[0], bits=8, parity=None, stop=1)
        while True:
            if uart.any():
                b = bytearray('000000', 'utf-8')
                uart.readinto(b)
                t = b.decode('utf-8')
                print(t)    
            time.sleep(.05)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        print('Done')
if __name__ == "__main__":
    main()
