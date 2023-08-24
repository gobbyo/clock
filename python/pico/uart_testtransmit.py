from machine import UART, Pin
import time
#note for this to work, the picos must have common ground

def main():
    #D=degree, P=percent, C=celsius, F=fahrenheit, R=clear
    testdata = ['1230', '23DC', '55DP', '1231', '73DF', '54DP']
    baudrate = [9600, 19200, 38400, 57600, 115200]
    led = Pin('LED', Pin.OUT)
    try:
        uart1 = UART(0, baudrate[0], tx=Pin(0), rx=Pin(1))
        uart1.init(baudrate[0], bits=8, parity=None, stop=1)
        print("UART1 is configured as : ", uart1)
        for t in testdata:
            uart1.write(bytearray(t, 'utf-8'))
            led.on()
            time.sleep(1)
            if uart1.any():
                b = bytearray('0000', 'utf-8')
                uart1.readinto(b)
                t = b.decode('utf-8')
                print(t)
            led.off()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        led.low()
        print('Done')

if __name__ == "__main__":
    main()
