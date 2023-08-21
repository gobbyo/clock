from machine import Pin
from dht11 import DHT11

pin = Pin(28, Pin.OUT, Pin.PULL_DOWN)
sensor = DHT11(pin)
print("Temperature: {0}C {1}F".format(round(sensor.temperature), round((sensor.temperature*1.8)+32)))
print("Humidity: {}%".format(round(sensor.humidity)))