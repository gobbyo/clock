from servo import sg90
import time

def main():
    servo = sg90(0)
    try:
        servo.move(90)
        time.sleep(1)
        servo.move(15)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        print('Done')

if __name__ == '__main__':
    main()