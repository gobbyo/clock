import config
import kineticDisplay

#picos must have common ground for uart to work
def main():
    conf = config.Config("conf.json")
    clock = kineticDisplay.kineticDisplay(conf)
    
    try:
        extend = clock.getExtendAngles(1)
        print("getExtendAngles(1)")
        print(extend)

        retract = clock.getRetractAngles(1)
        print("getRetractAngles(1)")
        print(retract)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        print('Done')
    

if __name__ == "__main__":
    main()
