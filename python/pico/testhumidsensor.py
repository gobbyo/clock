from machine import Pin
from dht11 import DHT11
import time

def main():
    switch = Pin(2, Pin.OUT, pull=None)
    read_sensor = True

    while read_sensor:
        try:
            pin = Pin(20, Pin.OUT, Pin.PULL_DOWN)
            switch.on()
            time.sleep(1)
            sensor = DHT11(pin)
            temp = round(sensor.temperature)
            humid = round(sensor.humidity)
            print("Temperature: {0}C {1}F".format(temp, round((temp*1.8)+32)))
            print("Humidity: {}%".format(humid))
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            read_sensor = False
        except Exception as e:
            print("Exception: {}".format(e))
        finally:
            switch.off()
            time.sleep(3)
if __name__ == "__main__":
    main()