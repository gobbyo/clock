from servodisplay import servoDigitDisplay
import config
import time

def updateDigit(digit,conf):
    prev = conf.read("previous")
    digit.setpreviousNumber(prev)

    i = conf.read("current")
    print("Current Number {0}".format(i))
    motion = conf.read("motion")
    print("Motion {0}".format(motion))
    if motion == 0:
        digit.paintFastNumber(i)
    else:
        digit.paintSlowNumber(i)
    print("Previous Number {0}".format(i))
    conf.write("previous",i)

    i += 1
    if i >= len(digit._segnum):
        i = 0
    conf.write("current",i)
    time.sleep(1)

def main():
    digit = servoDigitDisplay()
    conf = config.Config("digit.json")
    extend = conf.read("extend")
    retract = conf.read("retract")
    for i in range(0,7):
        digit._extendAngles[i] = extend[i]
        digit._retractAngles[i] = retract[i]
    try:
        #while True:
        for i in range(0,15):
            updateDigit(digit,conf)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        conf.write("previous",14)
        conf.write("current",0)
        digit.__del__()
        print('Done')

if __name__ == '__main__':
    main()