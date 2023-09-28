import kineticClock
import time
import config
import json
import urequests

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
    conf = config.Config("config.json")
    clock = kineticClock.kineticClock(conf)

    try:
        elapsedwaitDate = 10 #seconds
        elapsedwaitTemp = 25 #seconds
        elapsedwaitHumid = 35 #seconds
        elapsedwaitTime = 45 #seconds

        displayMilitaryTime = conf.read("displayMilitaryTime")
        wifiHourlySchedule = conf.read("wifiHourlySchedule")
        tempHumidMinuteSchedule = conf.read("tempHumidMinuteSchedule")
        print("wifiHourlySchedule = {0} hours".format(wifiHourlySchedule))
        print("tempHumidMinuteSchedule = {0} minutes".format(tempHumidMinuteSchedule))
        elapsedseconds = 0
        nextwifischedule = 0
        nexttemphumidschedule = 0

        if clock.connectWifi(conf):
            clock.syncClock(conf)
        
        nexttemphumidschedule = 0
        nextwifischedule = (round((clock._sync.rtc.datetime()[timeEnum.hours]/12)) + wifiHourlySchedule)%24 #hours

        while True:
            if clock.motion():
                print("motion on")
            #display time
            if (elapsedseconds > elapsedwaitTime) or (elapsedseconds < elapsedwaitDate):
                clock.displayTime(clock._sync, displayMilitaryTime)
                print("elapsedmins = {0}, elapsedseconds = {1}".format(clock._sync.rtc.datetime()[timeEnum.minutes], elapsedseconds))
                
                #sensor measurement
                print("nexttemphumidschedule = {0}".format(nexttemphumidschedule))
                if nexttemphumidschedule <= clock._sync.rtc.datetime()[timeEnum.minutes]:
                    nexttemphumidschedule = (clock._sync.rtc.datetime()[timeEnum.minutes] + tempHumidMinuteSchedule)%60 #minutes
                    print("--reading temp sensor--")
                    clock.setIndoorTemp(conf)
                    time.sleep(1)
                    clock.setOutdoorTemp(conf)
                    time.sleep(2)
                while elapsedseconds < elapsedwaitDate:
                    elapsedseconds = round(clock._sync.rtc.datetime()[timeEnum.seconds])
                    time.sleep(1)
                
                #wifi and time sync
                if nextwifischedule == clock._sync.rtc.datetime()[timeEnum.hours]:
                    print("wifischedule = {0}".format(nextwifischedule))
                    nextwifischedule = (round((clock._sync.rtc.datetime()[timeEnum.hours]/12)) + wifiHourlySchedule)%24 #hours
                    print("nextwifischedule = {0}".format(nextwifischedule))
                    print("--wifi and time sync--")
                    if clock.connectWifi(conf):
                        clock.syncClock(conf)
            
            #display date
            if (elapsedseconds >= elapsedwaitDate) and (elapsedseconds < elapsedwaitTemp):
                clock.displayDate()
                print("elapsedseconds = {0}".format(elapsedseconds))                
                while (elapsedseconds < elapsedwaitTemp):
                    time.sleep(1)
                    elapsedseconds = round(clock._sync.rtc.datetime()[timeEnum.seconds])

            #display temp
            if (elapsedseconds >= elapsedwaitTemp) and (elapsedseconds < elapsedwaitHumid):
                clock.displayTemp(conf)
                print("elapsedseconds = {0}".format(elapsedseconds))                
                while (elapsedseconds < elapsedwaitHumid):
                    time.sleep(1)
                    elapsedseconds = round(clock._sync.rtc.datetime()[timeEnum.seconds])

            #display humidity
            if (elapsedseconds >= elapsedwaitHumid) and (elapsedseconds < elapsedwaitTime):
                clock.displayHumidity(conf)
                print("elapsedseconds = {0}".format(elapsedseconds))
                while (elapsedseconds < elapsedwaitTime):
                    time.sleep(1)
                    elapsedseconds = round(clock._sync.rtc.datetime()[timeEnum.seconds])

            elapsedseconds = round(clock._sync.rtc.datetime()[timeEnum.seconds])
            print("elapsedseconds = {0}".format(elapsedseconds))
            time.sleep(1)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        clock.__del__()
        print('Done')

if __name__ == "__main__":
    main()