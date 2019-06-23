import machine
import neopixel
from utime import ticks_diff, ticks_ms, ticks_add, sleep_ms
#Auge1 0-11 Auge2 12-23 Kiemen1 24-x Kiemen2 x+1-y Inner y+1-max

PIXEL_COUNT = 180
np = neopixel.NeoPixel(machine.Pin(13), PIXEL_COUNT)
SAMPLE_COUNT = 600

class Module(object):
    def __init__(self, pixels, color=None, intensity=1.0):
        self.pixels = pixels
        self.color = color
        self.intensity = intensity

    def all_pixels(self, onoff=True):
        if onoff:
            color = self._color_intensity()
        else:
            color = (0, 0, 0)
        for pixel in self.pixels:
            np[pixel] = color

    def _color_intensity(self):
        return tuple(int(self.intensity * self.color[i]) for i in range(3))


class SoundIntensity:
    '''
    Map microphone input to intensities
    TODO maybe add weighted (new intensities are more important)
    '''
    def __init__(self):
        self.buffer = [0] * 1000 #  (for smoothing)
        self.index = 0
        self.adc = machine.ADC(machine.Pin(33))
        self.adc.atten(machine.ADC.ATTN_11DB)  # 3,6V input
        self.adc.width(machine.ADC.ADC_WIDTH_9Bit)  # 3,6V input

    def current_average(self):
        return sum(self.buffer) / len(self.buffer)

    def _new_value(self, val):
        '''
        :val: float from 0 to 1
        '''
        self.buffer[self.index] = val
        self.index = (self.index + 1) % len(self.buffer)

    def next(self):
        self._new_value(self.adc.read() / 512)
        return self.current_average()


class Gills:
    def __init__(self, lefts, rights):
        self.lefts = lefts
        self.rights = rights
        self.sound_intensity = SoundIntensity()

    def step(self, ticks):
        # get sound intensity
        avg_intensity = self.sound_intensity.next()
        print(avg_intensity)
        avg_intensity = 1.0

        for gill in self.lefts + self.rights:
            gill.intensity = avg_intensity
            gill.all_pixels()


class Gill(Module):
    '''
    Only ONE kieme
    '''
    def __init__(self, pixels, color, intensity):
        super(Gill, self).__init__(pixels, color, intensity)
        self.all_pixels()

    def step(self, ticks):
        pass



class Eye(Module):
    def __init__(self, pixels, color):
        super(Eye, self).__init__(pixels, color)
        self.blink_end = None
        self.blink_duration = 100
        self.all_pixels(True)

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
    left_eye = Eye(list(range(12)), (200, 0, 0))
    right_eye = Eye(list(range(12, 24)), (0, 200, 0))
    # gills
    gills_singles = [Gill(list(pixels), color=(200, 50, 100), intensity=1.0) for pixels in [range(24, 30), range(30, 36), range(36, 42), range(42, 48)]]
    gills = Gills(gills_singles, [])  # treat all as lefties for now...

    modules = [left_eye, right_eye, gills]

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


def debug_main():
    adc = machine.ADC(machine.Pin(33))
    adc.atten(machine.ADC.ATTN_11DB)  # 3,6V input
    adc.width(machine.ADC.WIDTH_12BIT)  # 3,6V input
    color = (0,5,20)
    for i in range(PIXEL_COUNT):
        np[i] = color
    np.write()
    max_val = 1
    while True:
        sum_val = 0
        val = []
        x = ticks_ms()
        y = 0
        y_max = 0
        for i in range(100000):
            a = adc.read()
            y += a
            y_max = max(a,y_max)

        print("The master value", y/100000, y_max)
        return

        for i in range(1000):
            val.append( adc.read() )
        print("ticks per iterations ", ticks_diff(ticks_ms(),x)/1000)
        mean_val = sum(val)/len(val)
        sum_val = sum([abs(x - mean_val) for x in val])
        print(sum_val)
        max_val = max(max_val, sum_val )
        for i in range(PIXEL_COUNT):
            np[i] = tuple(int(sum_val/max_val * x) for x in color)

        np.write()
        sleep_ms(1)

if __name__ == "__main__":
    #main()
    debug_main()