import kineticClock
import time
import config

class timeEnum():
    year = 0
    month = 1
    day = 2
    weekday = 3
    hours = 4
    minutes = 5
    seconds = 6
    subSeconds = 7

class scheduleEnum():
    time = 0
    date = 1
    temp = 2
    humid = 3
    updateClock = 4
    updateIndoor = 5
    updateOutdoor = 6

class schedule():
    secondsSchedule = []
    displayTime = [scheduleEnum.time,0,14]
    displayDate = [scheduleEnum.date,15,24]
    displayTemp = [scheduleEnum.temp,25,34]
    displayHumidity = [scheduleEnum.humid,35,44]
    displayLastTime = [scheduleEnum.time,45,59]

    minutesSchedule = []
    updateClock = [scheduleEnum.updateClock,59,1]
    updateIndoorTempHumidity = [scheduleEnum.updateIndoor,4,15]
    updateOutdoorTempHumidity = [scheduleEnum.updateOutdoor,10,6]

    def __init__(self) -> None:
        self.initSecondSchedule()
        self.initMinuteSchedule()
        
    def __del__(self):
        pass

    def initSecondSchedule(self):
        self.secondsSchedule.clear()
        for s in range(60):
            if s >= self.displayTime[1] and s <= self.displayTime[2]:
                self.secondsSchedule.append(self.displayTime[0])
            if s >= self.displayDate[1] and s <= self.displayDate[2]:
                self.secondsSchedule.append(self.displayDate[0])
            if s >= self.displayTemp[1] and s <= self.displayTemp[2]:
                self.secondsSchedule.append(self.displayTemp[0])
            if s >= self.displayHumidity[1] and s <= self.displayHumidity[2]:
                self.secondsSchedule.append(self.displayHumidity[0])
            if s >= self.displayLastTime[1] and s <= self.displayLastTime[2]:
                self.secondsSchedule.append(self.displayTime[0])

    def initMinuteSchedule(self):
        for i in range(60):
            self.minutesSchedule.append(-1)
        
        m = self.updateClock[1]
        while m < 60:
            self.minutesSchedule.pop(m)
            self.minutesSchedule.insert(m,self.updateClock[0])
            m += self.updateClock[2]

        m = self.updateIndoorTempHumidity[1]
        while m < 60:
            self.minutesSchedule.pop(m)
            self.minutesSchedule.insert(m,self.updateIndoorTempHumidity[0])
            m += self.updateIndoorTempHumidity[2]

        m = self.updateOutdoorTempHumidity[1]
        while m < 60:
            self.minutesSchedule.pop(m)
            self.minutesSchedule.insert(m,self.updateOutdoorTempHumidity[0])
            m += self.updateOutdoorTempHumidity[2]

    def clearNearFutureDuplicates(self, schedule, elapsedSeconds, scheduleEnumType):
        i = elapsedSeconds
        while schedule[i] == scheduleEnumType:
            schedule[i] = -1
            i += 1
            if i >= 60:
                break

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