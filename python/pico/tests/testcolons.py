from servocolons import servoColonsDisplay
import time

def main():
    colons = servoColonsDisplay()
    colons.extend(True, True)
    time.sleep(1)
    colons.retract(True, True)
    time.sleep(1)

if __name__ == '__main__':
    main()