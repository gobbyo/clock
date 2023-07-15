from machine import Pin, RTC
import network, rp2, time
import urequests
import json
import time
import secrets
import segmentdisplays

# the shift register is connected to the 4 digit, 7 segment display as follows:
#   Q0 = segment A
#   Q1 = segment B
#   Q2 = segment C
#   Q3 = segment D
#   Q4 = segment E
#   Q5 = segment F
#   Q6 = segment G
#   Q7 = segment DP
#   Q8 = digit 1
#   Q9 = digit 2
#   Q10 = digit 3
#   Q11 = digit 4
def start(segdisp):
    segmentdisplays.showbacknumber(segdisp)
    segmentdisplays.showbackfloat(segdisp)
    segmentdisplays.showforwardfloat(segdisp)
    segmentdisplays.showforwardnumber(segdisp)

def wificonnect():
    print("Connect to WiFi")
    rp2.country('US')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # set power mode to get WiFi power-saving off (if needed)
    wlan.config(pm = 0xa11140)

    wlan.connect(secrets.ssid, secrets.pwd)

    while not wlan.isconnected() and wlan.status() >= 0:
        print("connecting...")
        time.sleep(1)

def syncclock(rtc):
    print("Sync clock")
    try:
        externalIPaddress = urequests.get('https://api.ipify.org').text
    except:
        externalIPaddress = "45.115.204.194"
    finally:
        print("Obtaining external IP Address: {0}".format(externalIPaddress))
    
    timeAPI = "https://www.timeapi.io/api/Time/current/ip?ipAddress={0}".format(externalIPaddress)
    print(timeAPI)
    r = urequests.get(timeAPI)
    universal = json.loads(r.content)
    timeAPI = "https://www.timeapi.io/api/TimeZone/zone?timeZone={0}".format(universal["timeZone"])
    print(timeAPI)
    r = urequests.get(timeAPI)
    j = json.loads(r.content)
    t = (j["currentLocalTime"].split('T'))[1].split(':')
    rtc.datetime((int(universal["year"]), int(universal["month"]), int(universal["day"]), 0, int(t[0]), int(t[1]), int(universal["seconds"]), 0))

def main(): 
    try:
        rtc = RTC()
        segdisp = segmentdisplays.segdisplays()
        start(segdisp)

        wificonnect()
        syncclock(rtc)
        
        while True:
            hour = rtc.datetime()[4]
            #ampm = "AM"
            if(hour > 12):
                #ampm = "PM"
                hour -= 12
            segdisp.printclockfloat(rtc.datetime()[5],rtc.datetime()[6])
            segdisp.printnumber(hour)
            #print("{:0d}:{:0>2d} {:0s}".format(hour, rtc.datetime()[5], ampm))
            #time.sleep(60)
    except KeyboardInterrupt:
        print("stopping program")
    finally:
        print("Graceful exit")

if __name__ == "__main__":
    main()