import machine, neopixel
import math
from utime import ticks_diff, ticks_ms, ticks_add, sleep_ms


PIN = 27
NUM_PIXEL = 108
MAX_ITENSITY = 160

class Mirror:
    def __init__(self):
        self.np = neopixel.NeoPixel(machine.Pin(PIN), NUM_PIXEL)
        self.start_h = 0

        for i in range(NUM_PIXEL):
            r,g,b = hsv_to_rgb( int(self.start_h + i*(360. / NUM_PIXEL)) %360, 1, 1)

            self.np[i] = (r,g,b)

        self.np.write()
        self.change = False
        self.step_time = 100
        self.last_step = ticks_ms()
    def step(self, ticks):
        if abs(ticks_diff(self.last_step,ticks)) > self.step_time:
            self.start_h = (self.start_h +1) %360
            for i in range(NUM_PIXEL):
                r, g, b = hsv_to_rgb(int(self.start_h + i * (360. / NUM_PIXEL)) % 360, 1, 1)

                self.np[i] = (r, g, b)
            self.change = True

        if self.change:
            self.np.write()
            self.change = False



def hsv_to_rgb(h,s,v):
    h60 = h / 60.0
    c = s * v
    x = c * (1 - abs(h60 % 2 - 1))
    hi = int(h60) % 6
    r, g, b = 0, 0, 0
    if hi == 0:
        r, g, b = c, x, 0
    elif hi == 1:
        r, g, b = x, c, 0
    elif hi == 2:
        r, g, b = 0, c, x
    elif hi == 3:
        r, g, b = 0, x, c
    elif hi == 4:
        r, g, b = x, 0, c
    elif hi == 5:
        r, g, b = c, 0, x
    r, g, b = int(r * MAX_ITENSITY), int(g * MAX_ITENSITY), int(b * MAX_ITENSITY)
    return r, g, b


def main(mirror):

    while True:

        ticks = ticks_ms()

        mirror.step(ticks)


if __name__ == "__main__":
    mirror = Mirror()
    main(mirror)


