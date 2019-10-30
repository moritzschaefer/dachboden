from math import atan2

import ujson
from ak8963 import AK8963
from machine import I2C, Pin


class Compass:
    def __init__(self):
        self.i2c = I2C(-1, scl=Pin(22), sda=Pin(21), freq=400000)
        # activate magnetometer and bypass
        self.i2c.writeto_mem(104, 0x6B, b'\x01')
        self.i2c.writeto_mem(104, 0x37, b'\x02')
        self.i2c.writeto_mem(104, 0x6a, b'\x00')
        try:
            f = open('compass_calibraten', 'r')
            data = ujson.load(f)
            f.close()
            print('Using offset {} and scale {}'.format(data['offset'], data['scale']))
        except OSError:
            data = {
                'offset': (0, 0, 0),
                'scale': (1, 1, 1)
            }
        self.sensor = AK8963(self.i2c, offset=data['offset'], scale=data['scale'])

    def step(self, _):
        print("MPU9250 id: " + hex(self.sensor.whoami))

        print(atan2(self.sensor.magnetic[1], self.sensor.magnetic[0]))
        # print(self.sensor.gyro)
        # print(self.sensor.magnetic)

    def calibration(self):
        print('Calibrating compass')
        offset, scale = self.sensor.calibrate(count=256, delay=200)
        data = {
            'offset': offset,
            'scale': scale,
        }
        f = open('compass_calibraten', 'w')
        ujson.dump(data, f)
        f.close()
        print('Calibration done')
