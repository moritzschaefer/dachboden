import machine
import time
import servo as servoLib

def main():
    # The GPIO9 and GPIO12 is meant.
    # Don't use GPIO13, this bug is happening then https://github.com/espressif/esptool/issues/394
    servo_y = servoLib.Servo(machine.Pin(9), 50, 1000, 2000, 180)
    servo_x = servoLib.Servo(machine.Pin(12), 50, 1000, 2000, 180)
    while True:
        servo_y.write_angle(0)
        servo_x.write_angle(0)
        time.sleep(2)
        servo_y.write_angle(180)
        servo_x.write_angle(180)
        time.sleep(2)


if __name__ == '__main__':
    main()


def rectangle(servo_x, servo_y):
    while True:
        servo_x.write_angle(0)
        servo_y.write_angle(40)
        time.sleep(0.5)
        servo_x.write_angle(0)
        servo_y.write_angle(70)
        time.sleep(0.5)
        servo_x.write_angle(40)
        servo_y.write_angle(70)
        time.sleep(0.5)
        servo_x.write_angle(40)
        servo_y.write_angle(40)
        time.sleep(0.5)
