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
    baudrate = [9600, 19200, 38400, 57600, 115200]
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

    #[year, month, day, weekday, hours, minutes, seconds, subseconds]
    syncclock(rtc)
    uart1 = UART(0, baudrate[0], tx=Pin(0), rx=Pin(1))
    uart1.init(baudrate[0], bits=8, parity=None, stop=1)
    print("UART is configured as : ", uart1)
    
    try:
        while True:
            j = json.dumps(rtc.datetime())

            if(len(j) < 256):
                print("seconds = {0}".format(rtc.datetime()[6]))
                b = bytearray(str(rtc.datetime()[6] % 10), 'utf-8')
                uart1.write(b)
                
                #b = bytearray(j, 'utf-8')
                #uart1.write(b)
                time.sleep(3)
                #if uart1.any():
                #    uart1.readinto(b)
                #    dt = b.decode('utf-8')
                #    print(dt)
                #    time.sleep(1)
    except KeyboardInterrupt:
        uart1.deinit()
        print('KeyboardInterrupt')
    finally:
        print('Done')

if __name__ == "__main__":
    main()