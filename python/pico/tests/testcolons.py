from servocolons import servoColonsDisplay
import config
import time

def main():
    c = config.Config("config.json")
    colons = servoColonsDisplay(c)
    colons.extend(True, True)
    time.sleep(1)
    colons.retract(True, True)
    time.sleep(1)
    colons.__del__()

if __name__ == '__main__':
    main()