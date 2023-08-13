from servodisplay import servoDigitDisplay
import time

def main():
    digit = servoDigitDisplay()
    digit.servospeed = 0.05

    try:
        digit.extend(0)
        time.sleep(1)
        digit.retract(0)
        time.sleep(1)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        digit.__del__()
        print('Done')

if __name__ == '__main__':
    main()