from servodisplay import servoDigitDisplay
import time

extend = [5,10,10,10,0,20,20]
retract = [100,110,110,110,95,120,115]
servospeed = 0.05

def main():
    digit = servoDigitDisplay()
    digit.servospeed = servospeed

    for i in range(0,7):
        digit.extendAngles[i] = extend[i]
        digit.retractAngles[i] = retract[i]

    try:
        while True:
            for i in range(0,10):
                print("Number {0}".format(i))
                digit.paintNumber(i)
                time.sleep(2)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        digit.__del__()
        print('Done')

if __name__ == '__main__':
    main()