
# This file contains the enum for the UART commands
# Commands are used to set the time and configuration of the servoDigitDisplay
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
    fastspeed = 1
    slowspeed = 2
    retract = 3
    extend = 4
    current = 5
    previous = 6
    reset = "F"

#time setting for all digits
#digit | command | 0 | 1 | 2 | 3 |
#---------------------------------
#  4  | "0" | "0" | "7" | "4" | "9" |

#fastspeed setting for all digits
#digit | command | 0 | 1 | 2 | 3 |
#---------------------------------
#  0  | "1" | "F" | "F" | "F" | "F" |
#  1  | "1" | "F" | "F" | "F" | "F" |
#  2  | "1" | "F" | "F" | "F" | "F" |
#  3  | "1" | "F" | "F" | "F" | "F" |

#slowspeed setting for all digits
#digit | command | 0 | 1 | 2 | 3 |
#---------------------------------
#  0  | "2" | "F" | "F" | "F" | "F" |
#  1  | "2" | "F" | "F" | "F" | "F" |
#  2  | "2" | "F" | "F" | "F" | "F" |
#  3  | "2" | "F" | "F" | "F" | "F" |

#digit 1 retract angle setting, e.g. [105, 100, 95, 110, 100, 100, 110]
#digit | command | segment | angle hundreds | angle tens | angle ones |
#---------------------------------
#  1  | "3" | "0" | "1" | "0" | "5" |
#  1  | "3" | "1" | "1" | "0" | "0" |
#  1  | "3" | "2" | "0" | "9" | "5" |
#  1  | "3" | "3" | "1" | "1" | "0" |
#  1  | "3" | "4" | "1" | "0" | "0" |
#  1  | "3" | "5" | "1" | "0" | "5" |
#  1  | "3" | "6" | "1" | "1" | "0" |

#digit 1 retract angle setting, e.g. [105, 100, 95, 110, 100, 100, 110]
#digit | command | segment | angle hundreds | angle tens | angle ones |
#---------------------------------
#  1  | "3" | "0" | "1" | "0" | "5" |
#  1  | "3" | "1" | "1" | "0" | "0" |
#  1  | "3" | "2" | "0" | "9" | "5" |
#  1  | "3" | "3" | "1" | "1" | "0" |
#  1  | "3" | "4" | "1" | "0" | "0" |
#  1  | "3" | "5" | "1" | "0" | "5" |
#  1  | "3" | "6" | "1" | "1" | "0" |

#digit 1 extend angle setting, e.g. [20, 10, 10, 10, 10, 15, 20]
#digit | command | segment | angle hundreds | angle tens | angle ones |
#---------------------------------
#  1  |  "4" | "0" | "0" | "2" | "0" |
#  1  |  "4" | "1" | "0" | "1" | "0" |
#  1  |  "4" | "2" | "0" | "1" | "0" |
#  1  |  "4" | "3" | "0" | "1" | "0" |
#  1  |  "4" | "4" | "0" | "1" | "0" |
#  1  |  "4" | "5" | "0" | "1" | "5" |
#  1  |  "4" | "6" | "0" | "2" | "0" |

#digit 1 current value, e.g. 0
#digit | command | segment | angle hundreds | angle tens | angle ones |
#---------------------------------
#  1  |  "5" | "F" | "F" | "F" | "0" |

#digit 1 previous value, e.g. 14
#digit | command | segment | angle hundreds | angle tens | angle ones |
#---------------------------------
#  1  |  "6" | "F" | "F" | "F" | "14" |

#digit 1 reset config file to factory defaults
#digit configuration values are not reset
#digit | command | segment | angle hundreds | angle tens | angle ones |
#---------------------------------
#  1  |  "7" | "F" | "F" | "F" | "F" |