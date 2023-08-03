from machine import UART, Pin, PWM
from servodisplay import servoDigitDisplay
import time

hour_tens = 0
hour_ones = 1
minute_tens = 2
minute_ones = 3

#change this to hour_tens, hour_ones, minute_tens, or minute_ones
readnumerictime = minute_ones 
#change these values to match your servo's extend angles
#0 is fully extended
extend = [5,10,5,10,10,15,30] 
#change these values to match your servo's retract angles
#90 is the default retraction
retract = [110,110,110,115,110,125,125]  
servospeed = 0.01
uartsignalpausetime = 0.1 #seconds

#picos must have common ground for uart to work
def main():
    prev = -1
    baudrate = [9600, 19200, 38400, 57600, 115200]
    
    digit = servoDigitDisplay()
    digit._servospeed = servospeed
    digit.clearDisplay()

    for i in range(0,7):
        digit._extendAngles[i] = extend[i]
        digit._retractAngles[i] = retract[i]
    
    try:
        uart = UART(0, baudrate[0], rx=Pin(1))
        uart.init(baudrate[0], bits=8, parity=None, stop=1)
        while True:
            if uart.any():
                b = bytearray('0000', 'utf-8')
                uart.readinto(b)
                t = b.decode('utf-8')
                print("raw decode = {0}".format(t))
                if t.isdigit():
                    n = int(t[readnumerictime])
                    if prev != n:
                        print("paintNumber {0}".format(n))
                        digit.paintNumber(n)
                        prev = n
                if t.isalpha():
                    code = t[readnumerictime]
                    print("code {0}".format(code))
                    if code == 'c':
                        digit.clearDisplay()
                    if code == 't':
                        digit.testServos()
            time.sleep(uartsignalpausetime)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        digit.__del__()
        print('Done')
if __name__ == "__main__":
    main()
