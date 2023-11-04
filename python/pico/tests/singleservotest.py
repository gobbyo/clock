from servo import sg90
import time

def main():
    servo = sg90(29)
    try:
        servo.move(10)
        time.sleep(1)
        servo.move(95)
        time.sleep(1)
        servo.move(10)
        time.sleep(1)
        servo.move(95)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        print('Done')

if __name__ == '__main__':
    main()