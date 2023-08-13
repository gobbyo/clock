import hotspot as hs
import secrets
import machine

wifi = hs.hotspot("picowclock","12pclock")
wifi.run()
print("ssid={0} pwd={1}".format(secrets.ssid, secrets.pwd))
wifi.__del__()