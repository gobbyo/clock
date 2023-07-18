from machine import UART, Pin
import time

def main():
    baudrate = [9600, 19200, 38400, 57600, 115200]
    led = Pin(25, Pin.OUT)
    try:
        uart1 = UART(0, baudrate[0], tx=Pin(0), rx=Pin(1))
        uart1.init(baudrate[0], bits=8, parity=None, stop=1)
        uart2 = UART(1, baudrate[1], tx=Pin(8), rx=Pin(9))
        uart2.init(baudrate[1], bits=8, parity=None, stop=1)
        print("UART1 is configured as : ", uart1)
        print("UART2 is configured as : ", uart2)
        while True:
            #baudrates = [9600, 19200, 38400, 57600, 115200]

            uart1.write('On')
            uart2.write('High')
            led.on()
            time.sleep(1)
            #if uart1.any():
            #    s = uart1.readline().decode('utf-8')
            #    print("uart1 received = {0}".format(s))
            #if uart2.any():
            #    s = uart2.readline().decode('utf-8')
            #    print("uart2 received = {0}".format(s))
            uart1.write('Off')
            uart2.write('Low')
            led.off()
            time.sleep(1)
            #if uart1.any():
            #    s = uart1.readline().decode('utf-8')
            #    print("uart1 received = {0}".format(s))
            #if uart2.any():
            #    s = uart2.readline().decode('utf-8')
            #    print("uart2 received = {0}".format(s))
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        led.low()
        print('Done')

if __name__ == "__main__":
    main()
