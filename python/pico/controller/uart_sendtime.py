import kineticClock
import time
import config
from timeEnum import timeEnum
from scheduler import schedule, scheduleEnum


def main():
    conf = config.Config("config.json")
    clock = kineticClock.kineticClock(conf)

    try:
        if clock.connectWifi():
            clock.syncClock()
        
        clock.setIndoorTemp(conf)
        clock.setOutdoorTemp(conf)

        itinerary = schedule()
        lastMinute = 0
        lastHour = 0

        while True:
            elapsedSeconds = round(clock._sync.rtc.datetime()[timeEnum.seconds])
            elapsedMinutes = round(clock._sync.rtc.datetime()[timeEnum.minutes])
            elapsedHours = round(clock._sync.rtc.datetime()[timeEnum.hours])
            print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))
            #check state of switch
            clock.hybernate(conf)

            if elapsedMinutes != lastMinute:
                itinerary.initSecondSchedule()
                lastMinute = elapsedMinutes
                print("initSecondSchedule()")

            if elapsedHours != lastHour:
                itinerary.initMinuteSchedule()
                lastHour = elapsedHours
                print("initMinuteSchedule()")
            
            if itinerary.secondsSchedule[elapsedSeconds] == scheduleEnum.time:
                clock.displayTime(clock._sync)
                itinerary.clearNearFutureDuplicates(itinerary.secondsSchedule, elapsedSeconds, scheduleEnum.time)
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))

            if itinerary.secondsSchedule[elapsedSeconds] == scheduleEnum.date:
                clock.displayDate()
                itinerary.clearNearFutureDuplicates(itinerary.secondsSchedule, elapsedSeconds, scheduleEnum.date)
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))

            if itinerary.secondsSchedule[elapsedSeconds] == scheduleEnum.temp:
                clock.displayTemp(conf)
                itinerary.clearNearFutureDuplicates(itinerary.secondsSchedule, elapsedSeconds, scheduleEnum.temp)
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))

            if itinerary.secondsSchedule[elapsedSeconds] == scheduleEnum.humid:
                clock.displayHumidity(conf)
                itinerary.clearNearFutureDuplicates(itinerary.secondsSchedule, elapsedSeconds, scheduleEnum.humid)
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))
            
            if itinerary.minutesSchedule[elapsedMinutes] == scheduleEnum.updateClock:
                print("--updating clock--")
                if clock.connectWifi():
                    clock.syncClock()
                itinerary.minutesSchedule[elapsedMinutes] = -1
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))

            if itinerary.minutesSchedule[elapsedMinutes] == scheduleEnum.updateIndoor:
                print("--reading indoor temp sensor--")
                clock.setIndoorTemp(conf)
                itinerary.minutesSchedule[elapsedMinutes] = -1
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))

            if itinerary.minutesSchedule[elapsedMinutes] == scheduleEnum.updateOutdoor:
                print("--reading outdoor temp sensor--")
                clock.setOutdoorTemp(conf)
                itinerary.minutesSchedule[elapsedMinutes] = -1
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))
            
            time.sleep(1)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        clock.__del__()
        print('Done')

if __name__ == "__main__":
    main()