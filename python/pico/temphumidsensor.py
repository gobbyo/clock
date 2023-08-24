from machine import Pin
from dht11 import DHT11
import time

def main():
    pin = Pin(28, Pin.OUT, Pin.PULL_DOWN)
    read_sensor = True
    temp = 0
    humid = 0
    prev_temp = 0
    prev_humid = 0

    while read_sensor:
        try:
            sensor = DHT11(pin)
            temp = round(sensor.temperature)
            humid = round(sensor.humidity)
            if(temp != prev_temp):
                print("Temperature: {0}C {1}F".format(temp, round((temp*1.8)+32)))
                prev_temp = temp
            if(humid != prev_humid):
                print("Humidity: {}%".format(humid))
                prev_humid = humid
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            read_sensor = False
        except Exception as e:
            print("Exception: {}".format(e))
        finally:
            time.sleep(5)

if __name__ == "__main__":
    main()