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
            print("external ip address = {0}".format(clock._sync.externalIPaddress))
            g = urequests.get("http://ip-api.com/json/{0}".format(clock._sync.externalIPaddress))
            geo = json.loads(g.content)
            conf.write("lat",geo['lat'])
            conf.write("lon",geo['lon'])
            print("lat = {0}".format(geo['lat']))
            print("lon = {0}".format(geo['lon']))
        
        nexttemphumidschedule = 0
        nextwifischedule = (clock._sync.rtc.datetime()[timeEnum.hours] + wifiHourlySchedule)%24 #hours

        while True:
            #display time
            if (elapsedseconds > clock._elapsedwaitTime) or (elapsedseconds < clock._elapsedwaitSyncHumidTemp):
                clock.displayTime(clock._sync)
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
                while elapsedseconds < clock._elapsedwaitSyncHumidTemp:
                    elapsedseconds = round(clock._sync.rtc.datetime()[timeEnum.seconds])
                    time.sleep(1)
                
                #wifi and time sync
                if nextwifischedule <= clock._sync.rtc.datetime()[timeEnum.hours]:
                    nextwifischedule = (clock._sync.rtc.datetime()[timeEnum.hours] + wifiHourlySchedule)%24 #hours
                    print("--wifi and time sync--")
                    if clock.connectWifi(conf):
                        clock.syncClock(conf)
            
            #display date
            if (elapsedseconds >= clock._elapsedwaitDate) and (elapsedseconds < clock._elapsedwaitTemp):
                clock.displayDate()
                print("elapsedseconds = {0}".format(elapsedseconds))                
                while (elapsedseconds < clock._elapsedwaitTemp):
                    time.sleep(1)
                    elapsedseconds = round(clock._sync.rtc.datetime()[timeEnum.seconds])

            #display temp
            if (elapsedseconds >= clock._elapsedwaitTemp) and (elapsedseconds < clock._elapsedwaitHumid):
                clock.displayTemp(conf)
                print("elapsedseconds = {0}".format(elapsedseconds))                
                while (elapsedseconds < clock._elapsedwaitHumid):
                    time.sleep(1)
                    elapsedseconds = round(clock._sync.rtc.datetime()[timeEnum.seconds])

            #display humidity
            if (elapsedseconds >= clock._elapsedwaitHumid) and (elapsedseconds < clock._elapsedwaitTime):
                clock.displayHumidity(conf)
                print("elapsedseconds = {0}".format(elapsedseconds))
                while (elapsedseconds < clock._elapsedwaitTime):
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