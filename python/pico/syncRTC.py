from machine import Pin, RTC, PWM
import network, rp2
import urequests
import json
import time
import secrets

class syncRTC:
    externalIPaddressAPI = "https://api.ipify.org"
    connectedLED_pin = 28
    disconnectedLED_pin = 27
    ledlumins = int(65535/3) #1/3 of total brightness

    def __init__(self):
        self.rtc = RTC()
        self.externalIPaddress = "00.000.000.000"
        self.red_led = PWM(Pin(self.disconnectedLED_pin, Pin.OUT))
        self.green_led = PWM(Pin(self.connectedLED_pin, Pin.OUT))
        self.red_led.freq(1000)
        self.green_led.freq(1000)
        self.red_led.duty_u16(0)
        self.green_led.duty_u16(0)
        rp2.country('US') # ISO 3166-1 Alpha-2 code, eg US, GB, DE, AU

    def syncclock(self):
        print("Sync clock")
        print("Obtaining external IP Address")
        try:
            externalIPaddress = urequests.get(self.externalIPaddressAPI).text
            print("Obtained external IP Address: {0}".format(externalIPaddress))
            timeAPI = "https://www.timeapi.io/api/Time/current/ip?ipAddress={0}".format(externalIPaddress)
            r = urequests.get(timeAPI)
            z = json.loads(r.content)
            timeAPI = "https://www.timeapi.io/api/TimeZone/zone?timeZone={0}".format(z["timeZone"])
            print(timeAPI)
            rq = urequests.get(timeAPI)
            j = json.loads(rq.content)
            t = (j["currentLocalTime"].split('T'))[1].split(':')
            print(t)
            #[year, month, day, weekday, hours, minutes, seconds, subseconds]
            self.rtc.datetime((int(z["year"]), int(z["month"]), int(z["day"]), 0, int(t[0]), int(t[1]), int(z["seconds"]), 0))
        except:
            print("Unable to obtain external IP Address")
            time.sleep(1)
            self.red_led.duty_u16(0)
            time.sleep(1)
            self.red_led.duty_u16(self.ledlumins)
            return False
        finally:
            print("successfully updated RTC time")
            self.green_led.duty_u16(self.ledlumins)
            self.red_led.duty_u16(0)
            return True

    def __del__(self):
        self.red_led.duty_u16(0)
        self.green_led.duty_u16(0)

    def connectWiFi(self):
        # Red LED indicates we're in the process of connecting to WiFi
        # Green LED indicates we've successfully synced the clock
        self.green_led.duty_u16(0)
        self.red_led.duty_u16(self.ledlumins)
        try:
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            wlan.config(pm = 0xa11140)
            wlan.connect(secrets.ssid, secrets.pwd)

            while not wlan.isconnected() and wlan.status() >= 0:
                print("connecting...")
                time.sleep(1)

        except:
            print("Unable to connect to WiFi")
            return False
        finally:
            if(wlan.isconnected()):
                print("WiFi Connected")
                print(wlan.ifconfig())
                self.green_led.duty_u16(self.ledlumins)
                time.sleep(1)
                self.red_led.duty_u16(0)
                self.green_led.duty_u16(0)
                return True
            else:
                print("Unable to connect to WiFi")
                return False