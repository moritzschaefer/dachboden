import machine
import neopixel
from utime import ticks_diff, ticks_ms, ticks_add, sleep_ms
#Auge1 0-11 Auge2 12-23 Kiemen1 24-x Kiemen2 x+1-y Inner y+1-max

PIXEL_COUNT = 180
np = neopixel.NeoPixel(machine.Pin(13), PIXEL_COUNT)

class Module(object):
    def __init__(self, np, pixels, color=None):
        self.np = np
        self.pixels = pixels
        self.color = color

    def all_pixels(self, onoff=True, color=None):
        if onoff:
            if not color:
                color = self.color
            if not color:
                color = (100, 100, 100)
        else:
            color = (0, 0, 0)
        for pixel in self.pixels:
            np[pixel] = color

class Kieme(Module):
    '''
    Only ONE kieme
    '''
    def __init__(self, pixels, color):
        super(Kieme, self).__init__(np, pixels, color)
        self.all_pixels(True, color) 

    def step(self, ticks):
        pass
        


class Eye(Module):
    def __init__(self, np, pixels, color):
        super(Eye, self).__init__(np, pixels, color)
        self.blink_end = None
        self.blink_duration = 100
        self.all_pixels(True, color)

    def blink(self, ticks):
        print('blink')
        self.blink_end = ticks_add(ticks, self.blink_duration)
        self.all_pixels(False)

    def step(self, ticks):
        if self.blink_end is not None and ticks_diff(self.blink_end, ticks) < 0:
            print('blink end')
            self.all_pixels(True)
            self.blink_end = None


def cycle(np, pixel_count):
    for i in range(4 * pixel_count):
        for j in range(pixel_count):
            np[j] = (0, 0, 0)
        np[i % pixel_count] = (255, 255, 255)
        np.write()
        time.sleep(0.25)


def bounce(np, pixel_count):
    for i in range(4 * pixel_count):
        for j in range(pixel_count):
            np[j] = (0, 0, 128)
        if (i // pixel_count) % 2 == 0:
            np[i % pixel_count] = (0, 0, 0)
        else:
            np[pixel_count - 1 - (i % pixel_count)] = (0, 0, 0)
        np.write()
        time.sleep(0.60)

def all_switching(np, pixel_count):
    for j in range(pixel_count):
        np[j] = (0, 0, 0)
    for i in range(0, pixel_count,2):
        np[i % pixel_count] = (2, 4, 8)
    np.write()
    time.sleep(0.25)

    for j in range(pixel_count):
        np[j] = (0, 0, 0)
    for i in range(1, pixel_count,2):
        np[i % pixel_count] = (8, 4, 2)
    np.write()
    time.sleep(0.25)


def fade_in_out(np, pixel_count):
    for i in range(0, 4 * 256, 8):
        for j in range(pixel_count):
            if (i // 256) % 2 == 0:
                val = i & 0xff
            else:
                val = 255 - (i & 0xff)
            np[j] = (val, 0, 0)
        np.write()


def clear(np, pixel_count):
    for i in range(pixel_count):
        np[i] = (0, 0, 0)
    np.write()


def main():
    left_eye = Eye(np, list(range(12)), (200, 0, 0))
    right_eye = Eye(np, list(range(12, 24)), (0, 200, 0))
    modules = [left_eye, right_eye]

    i = 0

    while True:
        ticks = ticks_ms()

        if i % 100 == 0:
            left_eye.blink(ticks)

        for module in modules:
            module.step(ticks)


        np.write()
        i += 1
        sleep_ms(50)
        #all_switching(np, pixel_count)
        #cycle(rp, pixel_count)


if __name__ == "__main__":
    main()
