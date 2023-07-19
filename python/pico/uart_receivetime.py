from machine import UART, Pin, PWM
from servodisplay import servoDigitDisplay
import time

hour_tens = 0
hour_ones = 1
minute_tens = 2
minute_ones = 3

readnumerictime = minute_ones
extend = [5,10,10,10,0,20,20]
retract = [100,110,110,110,95,120,115]
servospeed = 0.01

ledbrightness = int(65535/2)

def main():
    prev = -1
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
        while True:
            if uart.any():
                b = bytearray('0000', 'utf-8')
                uart.readinto(b)
                t = b.decode('utf-8')
                print(t)
                n = int(t[readnumerictime])
                if prev != n:
                    print("paintNumber {0}".format(n))
                    digit.paintNumber(n)
                    prev = n
            time.sleep(3)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        led.duty_u16(0)
        digit.__del__()
        print('Done')
if __name__ == "__main__":
    main()
