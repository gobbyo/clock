# Filename: main.py
# Author: Jeff Beman
# Date: summer 2023
# This file is saved as main.py and uploaded onto the Pico W display controller
# This is the main entry point to the controller for the Kinetic Display
# All the files under the common folder are shared between the controller and the
# digit controllers.  The files under the controller folder are specific to the
# controller and the files under the digit folder are specific to the digit controllers.

import kineticDisplay
import time
import config
from timeEnum import timeEnum
from scheduler import schedule, scheduleEnum

# Main entry point for the controller
# This is the main loop that runs the display
# It is responsible for checking the time and updating the display
# It is also responsible for checking the state of the switch and the time, 
# putting the display into hybernation mode, checking the schedule and updating the display
# Note the code makes heavy use of the config file to store and retrieve state information
# in the event there is an unexpected power loss
def main():
    conf = config.Config("config.json")
    display = kineticDisplay.kineticDisplay(conf)

    try:
        display.admin()
        if display.connectWifi():
            display.syncClock()
        
        display.setIndoorTemp(conf)
        display.setOutdoorTemp(conf)

        itinerary = schedule()
        lastMinute = 0
        lastHour = 0

        while True:
            elapsedSeconds = round(display._sync.rtc.datetime()[timeEnum.seconds])
            elapsedMinutes = round(display._sync.rtc.datetime()[timeEnum.minutes])
            elapsedHours = round(display._sync.rtc.datetime()[timeEnum.hours])
            print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))
            #check state of switch
            display.hybernateSwitch(conf)
            #check state of time
            display.hybernateTime(conf)

            if elapsedMinutes != lastMinute:
                itinerary.initSecondSchedule()
                lastMinute = elapsedMinutes
                print("initSecondSchedule()")

            if elapsedHours != lastHour:
                itinerary.initMinuteSchedule()
                lastHour = elapsedHours
                print("initMinuteSchedule()")
            
            if itinerary.secondsSchedule[elapsedSeconds] == scheduleEnum.time:
                display.displayTime(display._sync)
                itinerary.clearNearFutureDuplicates(itinerary.secondsSchedule, elapsedSeconds, scheduleEnum.time)
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))

            if itinerary.secondsSchedule[elapsedSeconds] == scheduleEnum.date:
                display.displayDate()
                itinerary.clearNearFutureDuplicates(itinerary.secondsSchedule, elapsedSeconds, scheduleEnum.date)
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))

            if itinerary.secondsSchedule[elapsedSeconds] == scheduleEnum.temp:
                display.displayTemp(conf)
                itinerary.clearNearFutureDuplicates(itinerary.secondsSchedule, elapsedSeconds, scheduleEnum.temp)
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))

            if itinerary.secondsSchedule[elapsedSeconds] == scheduleEnum.humid:
                display.displayHumidity(conf)
                itinerary.clearNearFutureDuplicates(itinerary.secondsSchedule, elapsedSeconds, scheduleEnum.humid)
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))
            
            if itinerary.minutesSchedule[elapsedMinutes] == scheduleEnum.updateClock:
                print("--updating display--")
                if display.connectWifi():
                    display.syncClock()
                itinerary.minutesSchedule[elapsedMinutes] = -1
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))

            if itinerary.minutesSchedule[elapsedMinutes] == scheduleEnum.updateIndoor:
                print("--reading indoor temp sensor--")
                display.setIndoorTemp(conf)
                itinerary.minutesSchedule[elapsedMinutes] = -1
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))

            if itinerary.minutesSchedule[elapsedMinutes] == scheduleEnum.updateOutdoor:
                print("--reading outdoor temp sensor--")
                display.setOutdoorTemp(conf)
                itinerary.minutesSchedule[elapsedMinutes] = -1
                print("elapsed {0}:{1}:{2}".format(elapsedHours, elapsedMinutes, elapsedSeconds))
            
            time.sleep(1)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        display.__del__()
        print('Done')

if __name__ == "__main__":
    main()