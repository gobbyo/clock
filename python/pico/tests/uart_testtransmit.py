from machine import UART, Pin
import time
#note for this to work, the picos must have common ground

def main():
    led = Pin('LED', Pin.OUT)
    while True:
        #"retract": [100, 100, 100, 110, 100, 100, 110], 
        #"extend": [15, 20, 10, 20, 10, 15, 20],
        testdata = ['400749', '41FFF1', '41FFF0', '120105', '122095', '130010', '131010', '14FFFE','15FFF0','1FFFFF']
        baudrate = [9600, 19200, 38400, 57600, 115200]

        try:
            uart = UART(0, baudrate[0], tx=Pin(0), rx=Pin(1))
            uart.init(baudrate[0], bits=8, parity=None, stop=1)
            print("UART is configured as : ", uart)
            b = bytearray('000000', 'utf-8')
            
            for t in testdata:
                uart.write(bytearray(t, 'utf-8'))
                led.on()
                time.sleep(1)
                if uart.any() > 0:
                    uart.readinto(b)
                    t = str(b.decode('utf-8'))
                    print("raw decode = {0}".format(t))

                led.off()
                time.sleep(5)
                
        except KeyboardInterrupt:
            print('KeyboardInterrupt')
            return False
        finally:
            led.low()
            print('Done')

if __name__ == "__main__":
    main()
