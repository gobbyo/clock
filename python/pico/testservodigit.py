from servodisplay import servoDigitDisplay
import time

extend = [5,10,20,20,15,0,10]
retract = [95,90,105,100,95,90,90]
servospeed = 0.05

def main():
    digit = servoDigitDisplay()
    digit.servospeed = servospeed

    for i in range(0,7):
        digit._extendAngles[i] = extend[i]
        digit._retractAngles[i] = retract[i]
    try:
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