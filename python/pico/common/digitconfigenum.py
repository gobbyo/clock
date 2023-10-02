# Each digit is assigned a number, 0-3, with 0 being the leftmost digit 
# and 3 being the rightmost digit when facing the clock.
class hourMinutesEnum():
    hour_tens = 0
    hour_ones = 1
    minute_tens = 2
    minute_ones = 3

# This file contains the UART commands
# Commands are used to set the display value and configuration of the servoDigitDisplay
# Commands are 6 characters long
# The valid character set is 0-9, A-F
    # 0 = 	0011 1111   0x3F
    # 1 =	0000 0110   0x06
    # 2 =	0101 1011   0x5B
    # 3 =	0100 1111   0x4F
    # 4 =	0110 0110   0x66
    # 5 =	0110 1101   0x6D
    # 6 =	0111 1101   0x7D
    # 7 =	0000 0111   0x07
    # 8 =   0111 1111   0x7F
    # 9 =   0110 0111   0x67
    # A =   0110 0011   0x63  #degrees
    # B =   0101 1100   0x5C  #percent
    # C =   0011 1001   0x39  #celcius
    # D =   0111 0001   0x71  #farhenheit
    # E =   0000 0000   0x00  #clear
    # F =   1000 0000   0x00  #ignore
# The first character is the digit to be set, 0-3. Digit 4 is ALL digits.
# The second character is the command to be executed, 0-7.
# 3rd-6th characters are the data to be used for the command.
class uartCommandEnum():
    time = 0
    motion = 1
    retract = 2
    extend = 3
    current = 4
    previous = 5
    reset = 0x0F

#time setting for all digits
#digit | command | 0 | 1 | 2 | 3 |
#---------------------------------
#  4  | "0" | "0" | "7" | "4" | "9" |

#motion setting for all digits
#digit | command | 0 | 1 | 2 | 3 |
#---------------------------------
#  4  | "1" | "F" | "F" | "F" | 1 |
#  4  | "1" | "F" | "F" | "F" | 0 |

#digit 1 retract angle setting, e.g. [105, 100, 95, 110, 100, 100, 110]
#digit | command | segment | angle hundreds | angle tens | angle ones |
#---------------------------------
#  1  | "2" | "0" | "1" | "0" | "5" |
#  1  | "2" | "1" | "1" | "0" | "0" |
#  1  | "2" | "2" | "0" | "9" | "5" |
#  1  | "2" | "3" | "1" | "1" | "0" |
#  1  | "2" | "4" | "1" | "0" | "0" |
#  1  | "2" | "5" | "1" | "0" | "5" |
#  1  | "2" | "6" | "1" | "1" | "0" |

#digit 1 extend angle setting, e.g. [20, 10, 10, 10, 10, 15, 20]
#digit | command | segment | angle hundreds | angle tens | angle ones |
#---------------------------------
#  1  |  "3" | "0" | "0" | "2" | "0" |
#  1  |  "3" | "1" | "0" | "1" | "0" |
#  1  |  "3" | "2" | "0" | "1" | "0" |
#  1  |  "3" | "3" | "0" | "1" | "0" |
#  1  |  "3" | "4" | "0" | "1" | "0" |
#  1  |  "3" | "5" | "0" | "1" | "5" |
#  1  |  "3" | "6" | "0" | "2" | "0" |

#digit 1 current value, e.g. 0
#digit | command | segment | angle hundreds | angle tens | angle ones |
#---------------------------------
#  1  |  "4" | "F" | "F" | "F" | "0" |

#digit 1 previous value, e.g. 3
#digit | command | segment | angle hundreds | angle tens | angle ones |
#---------------------------------
#  1  |  "5" | "F" | "F" | "F" | "3" |

#All digits reset to default values
#digit | command | thousands | hundreds | tens | ones |
#---------------------------------
#  4  |  "F" | "F" | "F" | "F" | "F" |