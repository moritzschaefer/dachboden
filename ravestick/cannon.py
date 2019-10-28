'''
This module controls the lasercannon on the back of the manta. The main objective is to use the laser as a pointer to the home base (using GPS)
'''

from machine import Pin, Timer
from utime import ticks_add, ticks_diff, ticks_ms

ROTATION_STEPS = 2048  # so many steps for one rotation
DELAY_MS = 2


class Cannon:
    def __init__(self):
        self.current_angle = self.load_cannon_angle()  # 0 is front. clockwise counting to 2048
        self.timer = Timer(-1)
        self.motor_state = 0
        self.motor_pins = [Pin(pin, Pin.OUT) for pin in [16, 5, 4, 0]]
        self.next_tick = None
        for i in range(4):
            self.motor_pins[i].value(0)

    def store_cannon_angle(self, angle):
        f = open('cannon_angle', 'w')
        f.write(str(angle))
        f.close()

    def load_cannon_angle(self):
        try:
            f = open('cannon_angle', 'r')
            angle = int(f.read().strip())
            f.close()
            return angle
        except FileNotFoundError:
            return 0

    def rotate_to(self, angle):
        self.target_angle = angle
        self.clockwise = ((self.target_angle - self.current_angle) % ROTATION_STEPS) < (ROTATION_STEPS / 2)
        self.timer.init(mode=Timer.PERIODIC, callback=self.timer_event, period=2)
        self.next_tick = ticks_add(ticks_ms(), DELAY_MS)

    def full_rotation(self):
        self.target_angle = self.current_angle - 1
        self.clockwise = True
        self.timer.init(mode=Timer.PERIODIC, callback=self.timer_event, period=2)
        self.next_tick = ticks_add(ticks_ms(), DELAY_MS)

    def calibration_finish(self):
        '''
        Stop the current rotation and set current_rotation=0; for calibration..
        '''
        self.current_angle = 0
        self.next_ticks = None

    def step(self, ticks):
        if self.next_ticks and ticks_diff(self.next_tick, ticks) < 0:
            self.next_tick = ticks_add(ticks, 2)

            if self.current_angle == self.target_angle:
                # TODO: finish with motor state 0?
                self.next_ticks = None
            else:
                self.motor_pins[self.motor_state].value(0)
                if self.clockwise:
                    self.motor_state = (self.motor_state + 1) % 4
                    self.current_angle = (self.current_angle + 1) % ROTATION_STEPS
                else:
                    self.motor_state = (self.motor_state - 1) % 4
                    self.current_angle = (self.current_angle - 1) % ROTATION_STEPS

                self.motor_pins[self.motor_state].value(1)
