from servo import sg90
import time

def main():
    servo = sg90(2)
    try:
        servo.move(90)
        time.sleep(1)
        servo.move(0)
        time.sleep(1)
        servo.move(90)
        time.sleep(1)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        servo.__del__()
        print('Done')

if __name__ == '__main__':
    main()