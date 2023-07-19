from machine import Pin, RTC, UART, PWM
import network, rp2
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
    uartdigits = []
    rtc = RTC()
    # set your WiFi Country
    rp2.country('US')

    # Red LED indicates we're in the process of connecting to WiFi
    red_led = PWM(Pin(27, Pin.OUT))
    green_led = PWM(Pin(28, Pin.OUT))
    red_led.freq(1000)
    green_led.freq(1000)
    green_led.duty_u16(0)
    red_led.duty_u16(1000)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm = 0xa11140)
    wlan.connect(secrets.ssid, secrets.pwd)

    while not wlan.isconnected() and wlan.status() >= 0:
        print("connecting...")
        time.sleep(1)

    #[year, month, day, weekday, hours, minutes, seconds, subseconds]
    syncclock(rtc)

    green_led.duty_u16(1000)
    red_led.duty_u16(0)
    
    uarttime = UART(0, baudrate[0], tx=Pin(0), rx=Pin(1))
    uarttime.init(baudrate[0], bits=8, parity=None, stop=1)
        
    try:
        while True:
            j = json.dumps(rtc.datetime())

            if(len(j) < 256):
                s = "{0:02d}{1:02d}".format(rtc.datetime()[4], rtc.datetime()[5])
                print(s)
                b = bytearray(s, 'utf-8')
                uarttime.write(b)
                time.sleep(5)

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        for i in uartdigits:
            i.deinit()
        red_led.duty_u16(0)
        green_led.duty_u16(0)
        print('Done')

if __name__ == "__main__":
    main()