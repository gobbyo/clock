from servodisplay import servoDigitDisplay
import config
import time
import machine

paintFast = False

def updateDigit(digit,conf):
    prev = conf.read("previous")
    digit.setpreviousNumber(prev)

    i = conf.read("current")
    print("Current Number {0}".format(i))
    if paintFast:
        digit.paintFastNumber(i)
    else:
        digit.paintSlowNumber(i)
    print("Previous Number {0}".format(i))
    conf.write("previous",i)

    i += 1
    if i >= len(digit._segnum):
        i = 0
    conf.write("current",i)
    deepsleep = conf.read("deepsleep")
    if deepsleep == 1:
        machine.deepsleep(5000)
    else:
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
        while True:
            updateDigit(digit,conf)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        digit.__del__()
        print('Done')

if __name__ == '__main__':
    main()