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
    #TODO: make this list configurable
    displayTime = [scheduleEnum.time,0,14]
    displayDate = [scheduleEnum.date,15,24]
    displayTemp = [scheduleEnum.temp,25,34]
    displayHumidity = [scheduleEnum.humid,35,44]
    displayLastTime = [scheduleEnum.time,45,59]

    minutesSchedule = []
    #TODO: make this list configurable
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