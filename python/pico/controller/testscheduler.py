from machine import RTC
import time

class timeEnum():
    year = 0
    month = 1
    day = 2
    weekday = 3
    hours = 4
    minutes = 5
    seconds = 6
    subseconds = 7

def main():
    rtc = RTC()
    #[year, month, day, weekday, hours, minutes, seconds, subseconds]
    rtc.datetime((2023, 9, 19, 4, 11, 44, 0, 0))
    print("{0:02}:{1:02}".format(rtc.datetime()[timeEnum.hours],rtc.datetime()[timeEnum.minutes]))
    currentmins = rtc.datetime()[timeEnum.minutes]
    nextmins = (currentmins + 15)%60
    print("currentmins = {0}, nextmins = {1}".format(currentmins, nextmins))
    time.sleep(3)

if __name__ == '__main__':
    main()