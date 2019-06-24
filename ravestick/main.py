import machine
import neopixel
from utime import ticks_diff, ticks_ms, ticks_add, sleep_ms
import http_api_handler
import uhttpd
import uasyncio as asyncio

#Auge1 0-11 Auge2 12-23 Kiemen1 24-x Kiemen2 x+1-y Inner y+1-max

PIXEL_COUNT = 180
np = neopixel.NeoPixel(machine.Pin(13), PIXEL_COUNT)
SAMPLE_COUNT = 200  # TODO tweak
WINDOW_LENGTH = 50  # TODO tweak
NORMALIZER_LENGTH = 20 # TODO tweak


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
        self.long_term_buffer = [0.1] * NORMALIZER_LENGTH
        self.ltb_index = 0
        self.long_term_mean = 0.1
        self.buffer = [0] * WINDOW_LENGTH  #  (for smoothing)
        self.index = 0
        self.adc = machine.ADC(machine.Pin(33))
        self.adc.atten(machine.ADC.ATTN_11DB)  # 3,6V input
        self.adc.width(machine.ADC.WIDTH_12BIT)  # 3,6V input
        self.mean_voltage = 1000

    def current_average(self):
        summed = 0
        weight = WINDOW_LENGTH
        for i in range(self.index, -1, -1):
            summed += weight * self.buffer[i]
            weight -= 1

        for i in range(WINDOW_LENGTH - 1, self.index, -1):
            summed += weight * self.buffer[i]
            weight -= 1

        return summed / (WINDOW_LENGTH * (WINDOW_LENGTH +1) / 2)


    def _new_value(self, val):
        '''
        :val: float from 0 to 1
        '''
        self.buffer[self.index] = val
        self.index = (self.index + 1) % len(self.buffer)

    def next(self):
        power = 0
        mean = 0
        for i in range(SAMPLE_COUNT):
            a = self.adc.read()
            power += abs(a - self.mean_voltage)
            mean += a

        self._new_value(power / (SAMPLE_COUNT * self.mean_voltage))
        cur_val = self.current_average()
        self.mean_voltage = mean / SAMPLE_COUNT

        # add to long term average
        if self.index == 0:
            self.long_term_buffer[self.ltb_index] = cur_val
            self.ltb_index = (self.ltb_index + 1) % len(self.long_term_buffer)
            self.long_term_mean = sum(self.long_term_buffer) / len(self.long_term_buffer)
            print(cur_val)

        mi, ma = min(self.long_term_buffer), max(self.long_term_buffer)

        return min(1.0, max(0.01, (cur_val - mi) / max(0.05, ma - mi)))

        # return min(1.0, max(0.0, cur_val - (self.long_term_mean / 2)) * 20)  # TODO maybe also calculate the standard deviation and replace 20 with 1/std. Or do min/max normalization!?




class Gills:
    def __init__(self, lefts, rights):
        self.lefts = lefts
        self.rights = rights

    def step(self, ticks):
        pass

    def all_pixels(self, onoff=True):
        for gill in self.lefts + self.rights:
            gill.all_pixels(onoff)

    def update_intensities(self, intensity):
        for gill in self.lefts + self.rights:
            gill.intensity = intensity
        # print(intensity)
        self.all_pixels()

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


class ApiHandler:
    def __init__(self):
        pass
    
    def get(self, api_request):
        print(api_request)
        return {'foo': 'bar'}


async def main():
    left_eye = Eye(list(range(12)), (0, 0, 0))
    right_eye = Eye(list(range(12, 24)), (0, 0, 0))
    # gills
    gills_singles = [Gill(list(pixels), color=(100, 200, 10), intensity=1.0) for pixels in [range(24, 30), range(30, 36), range(36, 42), range(42, 48)]]
    gills = Gills(gills_singles, [])  # treat all as lefties for now...

    modules = [left_eye, right_eye, gills]
    sound = SoundIntensity()
    print('im here')

    i = 0

    while True:
        intensity = sound.next()

        gills.update_intensities(intensity)

        ticks = ticks_ms()

        if i % 100 == 0:
            left_eye.blink(ticks)

        for module in modules:
            module.step(ticks)

        np.write()
        i += 1
        asyncio.sleep(1)


if __name__ == "__main__":
    api_handler = http_api_handler.Handler([(['test'], ApiHandler())])
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    server = uhttpd.Server([('/api', api_handler)])
    server.run()
