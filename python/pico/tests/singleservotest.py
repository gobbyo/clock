from servo import sg90
import time

def main():
    servo = sg90(15)
    try:
        servo.move(10)
        time.sleep(1)
        servo.move(90)
        time.sleep(1)
        servo.move(10)
        time.sleep(1)
        servo.move(90)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        print('Done')

if __name__ == '__main__':
    main()