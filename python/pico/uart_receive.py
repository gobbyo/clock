from machine import UART, Pin, PWM
import time

ledbrightness = int(65535/2)

def main():
    baudrate = [9600, 19200, 38400, 57600, 115200]
    led = PWM(Pin(10))
    led.freq(1000)      # Set the frequency value
    
    try:
        uart = UART(1, baudrate[1], rx=Pin(9))
        uart.init(baudrate[1], bits=8, parity=None, stop=1)
        print("UART is configured as : ", uart)
        while True:
            if uart.any():
                s = uart.readline().decode('utf-8')
                print(s)
                if s == 'High':
                    led.duty_u16(ledbrightness) # Set the duty cycle, between 0-65535
                else:
                    led.duty_u16(0)
            else:
                pass
            
            time.sleep(.05)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        led.duty_u16(0)
        print('Done')
if __name__ == "__main__":
    main()
