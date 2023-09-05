from servodisplay import servoDigitDisplay
import config
import machine
import time

extend = [25,5,10,20,25,20,35]
retract = [115,95,110,110,110,115,120]

def main():

    digit = servoDigitDisplay()
    conf = config.Config("digit.json")

    for i in range(0,7):
        digit._extendAngles[i] = extend[i]
        digit._retractAngles[i] = retract[i]
    
    try:
        while True:
            prev = conf.read("previous")
            digit._previousNumber = digit.getArray(digit._segnum[prev])

            i = conf.read("current")
            digit.paintNumber(i)
            print("Number {0}".format(i))
            conf.write("previous",i)

            i += 1
            if i >= len(digit._segnum):
                i = 0
            conf.write("current",i)
            machine.deepsleep(2000)
            #time.sleep(2)
            prev = conf.read("previous")
            digit.repaintLEDs(prev)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        digit.__del__()
        print('Done')

if __name__ == '__main__':
    main()