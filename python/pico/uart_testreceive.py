from machine import UART, Pin
import time

#note for this to work, the picos must have common ground
def main():
    baudrate = [9600, 19200, 38400, 57600, 115200]
    
    try:
        uart1 = UART(0, baudrate[0], rx=Pin(1))
        uart1.init(baudrate[0], bits=8, parity=None, stop=1)
        uart2 = UART(1, baudrate[0], rx=Pin(5))
        uart2.init(baudrate[0], bits=8, parity=None, stop=1)
        while True:
            if uart1.any():
                b = bytearray('0000', 'utf-8')
                uart1.readinto(b)
                t = b.decode('utf-8')
                print(t)
            if uart2.any():
                b = bytearray('0000', 'utf-8')
                uart2.readinto(b)
                t = b.decode('utf-8')
                print(t)        
            time.sleep(.05)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        print('Done')
if __name__ == "__main__":
    main()
