from machine import Pin

#default pins for your Raspberry Pi Pico/PicoW
latchPin = 7 #RCLK
clockPin = 6 #SRCLK
dataPin = 8 #SER

# The shift register is a 74HC595
# This shiftregister class helps reduce the number of pins needed by the microcontroller
# This class also supports daisy chaining shift registers
# To use this class, you need to connect the shift register to your microcontroller
# The shift register is connected to the microcontroller as follows:
#   latchPin = 7 (RCLK pin 12 on 74HC595)
#   clockPin = 6 (SRCLK pin 11 on 74HC595)
#   dataPin = 8 (SER pin 14 on 74HC595)
# First, set the register size
# Next, set the register property in the class as an array, for example if the size is 8, then the register is [0,0,0,0,0,0,0,0]
# Then call the set_register() method to set the register
# To change the register, change the register property then call the set_register() method again

class shiftregister():
    def __init__(self) -> None:
        self.register = []
        self.latch = Pin(latchPin, Pin.OUT)
        self.clock = Pin(clockPin, Pin.OUT)
        self.data = Pin(dataPin, Pin.OUT)
    
    def __delete__(self):
        self.register = []
        self.setregister()
        self.latch.low()
        self.clock.low()
        self.data.low()

    #optional class to set the pins on your microcontroller
    def set_pins(self, latch_pin, clock_pin, data_pin):
        self.latch.low()
        self.clock.low()
        self.data.low()
        del(self.latch)
        del(self.clock)
        del(self.data)
        self.latch = Pin(latch_pin, Pin.OUT)
        self.clock = Pin(clock_pin, Pin.OUT)
        self.data = Pin(data_pin, Pin.OUT)
        
    def set_registerSize(self,size):
        for i in range(size):
            self.register.append(0)

    def set_register(self):
        #open latch for data
        self.clock.low()
        self.latch.low()
        self.clock.high()

        #load data in register
        for i in range(len(self.register)-1, -1, -1):
            self.clock.low()
            if self.register[i] == 1:
                self.data.high()
            else:
                self.data.low()
            self.clock.high()

        #close latch for data
        self.clock.low()
        self.latch.high()
        self.clock.high()