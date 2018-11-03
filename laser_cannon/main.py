import machine
import time

import mpu6050

FACTOR = 100
SERVO_LIMITS = range(50, 105)


def main():
    x = 75
    y = 75

    x_servo = machine.PWM(machine.Pin(12), 50)
    y_servo = machine.PWM(machine.Pin(14), 50)

    mpu6050_i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))

    accelerometer = mpu6050.accel(mpu6050_i2c)


    last_v = accelerometer.get_values()

    while True:
        v = accelerometer.get_values()

        # values range from -17000 to +17000
        new_x = int((((v['AcY'] + 17000) / 34000) * (len(SERVO_LIMITS))) + min(SERVO_LIMITS))
        new_y = int((((v['AcX'] + 17000) / 34000) * (len(SERVO_LIMITS))) + min(SERVO_LIMITS))

        # y_diff = v['AcX'] - last_v['AcX']
        # x_diff = v['AcY'] - last_v['AcY']

        # new_x = x + x_diff / FACTOR
        # new_y = y + y_diff / FACTOR

        if new_x in SERVO_LIMITS:
            x_servo.duty(new_x)
        if new_y in SERVO_LIMITS:
            y_servo.duty(new_y)

        last_v = v
        time.sleep_ms(30)


if __name__ == '__main__':
    main()
