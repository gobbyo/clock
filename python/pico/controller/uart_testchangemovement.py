from machine import UART, Pin
import time
#note for this to work, the picos must have common ground

def main():
    #PicoWireless
    switch = Pin(22, Pin.IN, Pin.PULL_UP)
    LED = 25 #'LED' # PicoWireless
                    # 25 is the onboard LED for the Pico
    led = Pin(LED, Pin.OUT)
    #"retract": [100, 100, 100, 110, 100, 100, 110], 
    #"extend": [15, 20, 10, 20, 10, 15, 20],
    movement = ['41FFF0']
    baudrate = [9600, 19200, 38400, 57600, 115200]

    while switch.value() == 1:
        print("waiting for switch")
        time.sleep(1)

    try:
        uart = UART(0, baudrate[0], tx=Pin(12), rx=Pin(13))
        uart.init(baudrate[0], bits=8, parity=None, stop=1)
        print("UART is configured as : ", uart)
        b = bytearray('000000', 'utf-8')
        
        for t in movement:
            uart.write(bytearray(t, 'utf-8'))
            led.on()
            time.sleep(1)
            if uart.any() > 0:
                uart.readinto(b)
                t = str(b.decode('utf-8'))
                print("raw decode = {0}".format(t))

            led.off()
            time.sleep(1)
                
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
        return False
    finally:
        led.low()
        print('Done')

if __name__ == "__main__":
    main()
