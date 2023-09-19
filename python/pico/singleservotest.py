from servo import sg90
import time

def main():
    servo = sg90(6)
    try:
        servo.move(20)
        time.sleep(1)
        servo.move(100)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        print('Done')

if __name__ == '__main__':
    main()