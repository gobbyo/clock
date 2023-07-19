from machine import UART, Pin, PWM
from servodisplay import servoDigitDisplay
import time

extend = [5,10,10,10,0,20,20]
retract = [100,110,110,110,95,120,115]
servospeed = 0.01

ledbrightness = int(65535/2)

def main():
    prev = 0
    baudrate = [9600, 19200, 38400, 57600, 115200]
    led = PWM(Pin(10))
    led.freq(1000)      # Set the frequency value
    
    digit = servoDigitDisplay()
    digit.servospeed = servospeed
    digit.clearDisplay()

    for i in range(0,7):
        digit.extendAngles[i] = extend[i]
        digit.retractAngles[i] = retract[i]
    
    try:
        uart = UART(0, baudrate[0], rx=Pin(1))
        uart.init(baudrate[0], bits=8, parity=None, stop=1)
        print("UART is configured as : ", uart)
        while True:
            if uart.any():
                b = bytearray('00', 'utf-8')
                uart.readinto(b)
                try:
                    n = int(b.decode('utf-8'))
                    if prev != n:
                        print("Number {0}".format(n))
                        digit.paintNumber(n % 10)
                        prev = n
                finally:
                    pass
            time.sleep(1)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        led.duty_u16(0)
        digit.__del__()
        print('Done')
if __name__ == "__main__":
    main()
