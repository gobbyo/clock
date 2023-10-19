from machine import RTC
import network
import urequests
import json
import time
import machine

externalIPAddressAPI=const("http://api.ipify.org")
class syncRTC:

    def __init__(self):
        self.rtc = RTC()
        self.externalIPaddress = "00.000.000.000"

    def syncclock(self):
        print("Sync clock")
        returnval = True

        try:
            self.setExternalIPAddress()
            timeAPI = "https://www.timeapi.io/api/Time/current/ip?ipAddress={0}".format(self.externalIPaddress)
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
        except Exception as e:
            print("Exception: {}".format(e))
            returnval = False
        finally:
            return returnval

    def __del__(self):
        urequests.Response.close()
        #machine.reset()

    def setExternalIPAddress(self):
        try:
            print("Obtaining external IP Address")
            ipaddress = urequests.get(externalIPAddressAPI)
            self.externalIPaddress = ipaddress.content.decode("utf-8")
            print("Obtained external IP Address: {0}".format(self.externalIPaddress))
        except Exception as e:
            print("Exception: {}".format(e))
        finally:
            pass

    def connectWiFi(self, ssid, pwd):
        try:
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            # set power mode to get WiFi power-saving off (if needed)
            wlan.config(pm = 0xa11140)
            #print("Connecting to WiFi, ssid={0}, pwd={1}".format(secrets.ssid, secrets.pwd))
            wlan.connect(ssid, pwd)

            while not wlan.isconnected() and wlan.status() >= 0:
                print("connecting...")
                time.sleep(1)

        except:
            print("Unable to connect to WiFi")
        finally:
            if(wlan.isconnected()):
                print("WiFi Connected")
                print(wlan.ifconfig())
                time.sleep(1)
                return True
            else:
                print("Unable to connect to WiFi")
                return False