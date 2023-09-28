import kineticClock
import time
import config
from timeEnum import timeEnum
from scheduler import schedule, scheduleEnum


def main():
    conf = config.Config("config.json")
    clock = kineticClock.kineticClock(conf)

    try:
        display24Hour = conf.read("display24Hour")

        if clock.connectWifi():
            clock.syncClock(conf)
        
        clock.setIndoorTemp(conf)
        clock.setOutdoorTemp(conf)
        clock.motion()

        itinerary = schedule()
        lastMinute = 0
        lastHour = 0

        while True:
            elapsedSeconds = round(clock._sync.rtc.datetime()[timeEnum.seconds])
            elapsedMinutes = round(clock._sync.rtc.datetime()[timeEnum.minutes])
            elapsedHours = round(clock._sync.rtc.datetime()[timeEnum.hours])
            #print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))

            if elapsedMinutes != lastMinute:
                itinerary.initSecondSchedule()
                print("initSecondSchedule()")
                lastMinute = elapsedMinutes

            if elapsedHours != lastHour:
                itinerary.initMinuteSchedule()
                print("initMinuteSchedule()")
                lastHour = elapsedHours
            
            if itinerary.secondsSchedule[elapsedSeconds] == scheduleEnum.time:
                clock.displayTime(clock._sync)
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))
                itinerary.clearNearFutureDuplicates(itinerary.secondsSchedule, elapsedSeconds, scheduleEnum.time)

            if itinerary.secondsSchedule[elapsedSeconds] == scheduleEnum.date:
                clock.displayDate()
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))
                itinerary.clearNearFutureDuplicates(itinerary.secondsSchedule, elapsedSeconds, scheduleEnum.date)

            if itinerary.secondsSchedule[elapsedSeconds] == scheduleEnum.temp:
                clock.displayTemp(conf)
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))
                itinerary.clearNearFutureDuplicates(itinerary.secondsSchedule, elapsedSeconds, scheduleEnum.temp)

            if itinerary.secondsSchedule[elapsedSeconds] == scheduleEnum.humid:
                clock.displayHumidity(conf)
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))
                itinerary.clearNearFutureDuplicates(itinerary.secondsSchedule, elapsedSeconds, scheduleEnum.humid)
            
            if itinerary.minutesSchedule[elapsedMinutes] == scheduleEnum.updateClock:
                print("--updating clock--")
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))
                if clock.connectWifi():
                    clock.syncClock(conf)
                itinerary.minutesSchedule[elapsedMinutes] = -1

            if itinerary.minutesSchedule[elapsedMinutes] == scheduleEnum.updateIndoor:
                print("--reading indoor temp sensor--")
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))
                clock.setIndoorTemp(conf)
                itinerary.minutesSchedule[elapsedMinutes] = -1

            if itinerary.minutesSchedule[elapsedMinutes] == scheduleEnum.updateOutdoor:
                print("--reading outdoor temp sensor--")
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))
                clock.setOutdoorTemp(conf)
                itinerary.minutesSchedule[elapsedMinutes] = -1
            
            #check switch to see if state has changed
            clock.motion()
            
            #check switch to see if state has changed
            display24Hour = conf.read("display24Hour")
            
            time.sleep(1)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        clock.__del__()
        print('Done')

if __name__ == "__main__":
    main()