from servodisplay import servoDigitDisplay
import time

extend = [5,5,5,10,10,5,30]
retract = [110,105,110,115,110,120,130]
servospeed = 0.05

def main():
    digit = servoDigitDisplay()
    digit.servospeed = servospeed

    for i in range(0,7):
        digit._extendAngles[i] = extend[i]
        digit._retractAngles[i] = retract[i]
    try:
        while True:
            for i in range(0,len(servoDigitDisplay._segnum)):
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