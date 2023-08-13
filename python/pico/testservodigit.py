from servodisplay import servoDigitDisplay
import time

extend = [5,5,5,10,10,5,30]
retract = [100,105,110,110,110,120,125]
servospeed = 0.05

def main():
    digit = servoDigitDisplay()
    digit.servospeed = servospeed

    for i in range(0,7):
        digit._extendAngles[i] = extend[i]
        digit._retractAngles[i] = retract[i]
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