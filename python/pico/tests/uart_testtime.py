from machine import Pin,UART
import digitfourdisplay595

def main():
    print("main")
    display = digitfourdisplay595.digitdisplay()
    display.setPins([3,2,1,0],7,6,8)

    baudrate = [9600, 19200, 38400, 57600, 115200]

    try:
        uart = UART(0, baudrate[0], tx=Pin(12), rx=Pin(13))
        uart.init(baudrate[0], bits=8, parity=None, stop=1)
        f = 0
        b = bytearray('0000', 'utf-8')
        while True:
            if uart.any():
                print("uart.any()")
                uart.readinto(b)
                print(b)
                t = b.decode('utf-8')
                print(t)
                if (len(t) == 4):
                    if t.isdigit():
                        f = float("{0}{1}.{2}{3}".format(t[0],t[1],t[2],t[3]))
            display.printfloat(f)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        print('Done')

if __name__ == '__main__':
    main()