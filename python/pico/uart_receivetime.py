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
extend = [20,10,15,20,15,20,35] 
#change these values to match your servo's retract angles
#90 is the default retraction
retract = [115,90,105,100,95,110,120]
servospeed = 0.01
uartsignalpausetime = 10 #seconds

#picos must have common ground for uart to work
def main():
    prev = -1
    baudrate = [9600, 19200, 38400, 57600, 115200]
    
    digit = servoDigitDisplay()
    digit._servospeed = servospeed
    digit.paintNumber(0x0E)

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
                    #machine.deepsleep(50000)
            time.sleep(uartsignalpausetime)
            #machine.deepsleep(5000)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        digit.__del__()
        print('Done')
if __name__ == "__main__":
    main()
