import machine
import time
import servo as servoLib


def main():
    servo = servoLib.Servo(machine.Pin(13), 50, 1000, 2000, 180)
    while True:
        servo.write_angle(0)
        time.sleep(2)
        servo.write_angle(180)
        time.sleep(2)


if __name__ == '__main__':
    main()
