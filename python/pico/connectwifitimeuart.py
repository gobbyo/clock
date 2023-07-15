from machine import Pin, RTC, UART
import network, rp2, time
import urequests
import json
import time
import secrets


def syncclock(rtc):
    print("Sync clock")
    print("Obtaining external IP Address")
    externalIPaddress = "45.115.204.194" #default
    try:
        externalIPaddress = urequests.get('https://api.ipify.org').text
        print("Obtained external IP Address: {0}".format(externalIPaddress))
    except:
        print("Unable to obtain external IP Address, using default: {0}".format(externalIPaddress))
    
    timeAPI = "https://www.timeapi.io/api/Time/current/ip?ipAddress={0}".format(externalIPaddress)
    r = urequests.get(timeAPI)
    z = json.loads(r.content)
    timeAPI = "https://www.timeapi.io/api/TimeZone/zone?timeZone={0}".format(z["timeZone"])
    print(timeAPI)
    rq = urequests.get(timeAPI)
    j = json.loads(rq.content)
    t = (j["currentLocalTime"].split('T'))[1].split(':')
    #[year, month, day, weekday, hours, minutes, seconds, subseconds]
    rtc.datetime((int(z["year"]), int(z["month"]), int(z["day"]), 0, int(t[0]), int(t[1]), int(z["seconds"]), 0))

def main():
    rtc = RTC()
    # set your WiFi Country
    rp2.country('US')

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # set power mode to get WiFi power-saving off (if needed)
    wlan.config(pm = 0xa11140)

    wlan.connect(secrets.ssid, secrets.pwd)

    while not wlan.isconnected() and wlan.status() >= 0:
        print("connecting...")
        time.sleep(1)

    syncclock(rtc)
    uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
    uart.init(9600, bits=8, parity=None, stop=1)
    print("UART is configured as : ", uart)

    try:
        while True:
            j = json.dumps(rtc.datetime())
            
            if(len(j) < 256):
                b = bytearray(j, 'utf-8')
                uart.write(b)
                time.sleep(1)
                if uart.any():
                    uart.readinto(b)
                    dt = b.decode('utf-8')
                    #[year, month, day, weekday, hours, minutes, seconds, subseconds]
                    print(dt)
                    time.sleep(1)
    except KeyboardInterrupt:
        uart.deinit()
        print('KeyboardInterrupt')
    finally:
        print('Done')

if __name__ == "__main__":
    main()