def decodeHex(value):
    returnVal = value
    if value == "A":
        returnVal = 10
    elif value == "B":
        returnVal = 11
    elif value == "C":
        returnVal = 12
    elif value == "D":
        returnVal = 13
    elif value == "E":
        returnVal = 14
    elif value == "F":
        returnVal = 15
    return returnVal

def encodeHex(value):
    if value < 10:
        return str(value)
    if value > 16:
        return 'F'
    return str(hex(value)).upper()[2:]

def validate(value):
    print("validate(len({0}))".format(len(value)))
    if len(value) != 6:
        return False
    for d in value:
        #print("validate({0})".format(decodeHex(d)))
        try:
            i = int(decodeHex(d))
            if (i < 0) or (i > 15):
                print("validate: invalid value {0}".format(i))
                return False
        except:
            print("validate: invalid value {0}".format(value))
            return False
        finally:
            pass
    return True