from servo import sg90
import time

def main():
    servo = sg90(17)
    try:
        servo.move(10)
        time.sleep(1)
        servo.move(110)
        time.sleep(1)
        servo.move(10)
        time.sleep(1)
        servo.move(110)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        print('Done')

if __name__ == '__main__':
    main()