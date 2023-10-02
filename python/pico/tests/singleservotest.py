from servo import sg90
import time

def main():
    servo = sg90(10)
    try:
        servo.move(0)
        time.sleep(1)
        servo.move(90)
        time.sleep(1)
        servo.move(0)
        for i in range(0, 180, 3):
            servo.move(i)
            time.sleep(0.1)
        servo.move(0)
        time.sleep(1)
        servo.move(90)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    finally:
        print('Done')

if __name__ == '__main__':
    main()