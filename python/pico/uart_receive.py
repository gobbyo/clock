from machine import UART, Pin, PWM
from servodisplay import servoDigitDisplay
import time

readnumerictime = 3
extend = [5,10,10,10,0,20,20]
retract = [100,110,110,110,95,120,115]
servospeed = 0.01

ledbrightness = int(65535/2)

def main():
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
                b = bytearray('0000', 'utf-8')
                uart.readinto(b)
                t = b.decode('utf-8')
                print("Number {0}".format(t[readnumerictime]))
                digit.paintNumber(t[readnumerictime])
            time.sleep(3)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        led.duty_u16(0)
        digit.__del__()
        print('Done')
if __name__ == "__main__":
    main()
