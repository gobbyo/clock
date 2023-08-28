from servodisplay import servoDigitDisplay
import time

extend = [25,5,10,10,15,25,35]
retract = [115,95,110,100,105,115,120]
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
                time.sleep(1)
            time.sleep(2)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        digit.__del__()
        print('Done')

if __name__ == '__main__':
    main()