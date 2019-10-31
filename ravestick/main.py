import gc
from math import sin

import http_api_handler
import machine
import micropython
import neopixel
import uasyncio as asyncio
import uhttpd
from cannon import Cannon
from compass import Compass
from sound_intensity import SoundIntensity
from utime import ticks_add, ticks_diff, ticks_ms

#Auge1 0-11 Auge2 12-23 Kiemen1 24-x Kiemen2 x+1-y Inner y+1-max

PIXEL_COUNT = 180
np = neopixel.NeoPixel(machine.Pin(13), PIXEL_COUNT)
EYE_WIDTH = 3
EYES_STEPTIME = 100
STROBE_LENGTH = 10
STROBE_TOTAL = 5000
#GILLS_PULSETIME = 5000
PULSE_FACTOR = 0.0005


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


class Gills:
    def __init__(self, lefts, rights):
        self.lefts = lefts
        self.rights = rights
        self.mode = 'normal'
        self.next_tick = None

    def step(self, ticks):
        if self.mode == 'strobo':
            if ticks_diff(self.next_tick, ticks) < 0:
                for gill in self.lefts + self.rights:
                    if self._strobo_on:
                        gill.intensity = 0
                        self.next_tick = (ticks_add(ticks, STROBE_LENGTH * 3))
                    else:
                        gill.intensity = 1
                        self.next_tick = (ticks_add(ticks, STROBE_LENGTH))
                self._strobo_on = not self._strobo_on
                if ticks_diff(self.last_tick, ticks) < 0:
                    self.setmode(self._last_mode)

                # print(intensity)
                self.all_pixels()

    def all_pixels(self, onoff=True):
        for gill in self.lefts + self.rights:
            gill.all_pixels(onoff)

    def update_intensities(self, intensity):
        if self.mode == 'normal':
            for gill in self.lefts + self.rights:
                gill.intensity = intensity
            # print(intensity)
            self.all_pixels()

    def setmode(self, mode, value=0.3):
        self._last_mode = self.mode
        self.mode = mode
        if mode == 'strobo':
            self._strobo_on = False
            for gill in self.lefts + self.rights:
                gill.color = (100, 100, 100)
                self.next_tick = ticks_ms()
                self.last_tick = ticks_add(ticks_ms(), STROBE_TOTAL)
        elif mode == 'normal':
            for gill in self.lefts + self.rights:
                gill.color = (0, 0, 20)
        elif mode == 'color':
            for gill in self.lefts + self.rights:
                gill.intensity = value
                gill.color = (0, 0, 20)
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
        self.blink_duration = 150
        self.all_pixels(True)
        self.color_loop = False
        self.eye_time = ticks_ms()
        self.eye_pos = 0

    def blink(self):
        self.blink_end = ticks_add(ticks_ms(), self.blink_duration)
        self.all_pixels(False)

    def step(self, ticks):
        if not self.color_loop:
            if self.blink_end is not None and ticks_diff(self.blink_end, ticks) < 0:
                self.all_pixels(True)
                self.blink_end = None
        else:
            self.pulse_eye(ticks)

    def pulse_eye(self, ticks):
        self.intensity = (sin(PULSE_FACTOR * abs(ticks_diff(ticks,self.eye_time))) + 1.2 )/ 2.2
        self.all_pixels(True)

    def rotating_eye(self, ticks):
        eye_percentage = abs(ticks_diff(self.eye_time, ticks)) / float(EYES_STEPTIME)
        if eye_percentage >= 1:
            self.eye_time = ticks_ms()
            self.eye_pos = (self.eye_pos + 1) % 12
            eye_percentage = 1
        for p in self.pixels:
            np[p] = (0,0,0)
        for i in range(EYE_WIDTH):
            if i == 0:
                np[self.pixels[0] + self.eye_pos] = tuple(int((1 - eye_percentage) * x) for x in self.color)
            elif i == (EYE_WIDTH - 1):
                np[self.pixels[0] + ((i + self.eye_pos) % 12)] = tuple(int(eye_percentage * x) for x in self.color)
            else:
                np[self.pixels[0] + ((i + self.eye_pos) % 12)] = self.color


class ApiHandler:
    def __init__(self, modules):
        self.modules = modules

    def index(self):
        f = open('index.html', 'r')
        html = f.read()
        f.close()
        return html

    def get(self, api_request):
        print(api_request)
        # TODO Not sure if bullshit or handled right, see https://github.com/fadushin/esp8266/tree/master/micropython/uhttpd  Api Handlers... Inputs
        operation =  api_request['query_params'].get('operation', 'index')
        if 'left_eye' == operation:
            self.modules['left_eye'].blink()
        elif 'right_eye' == operation:
            self.modules['right_eye'].blink()
        elif 'strobo' == operation:
            self.modules['gills'].setmode('strobo')
        elif 'color_loop'  == operation:
            value = int(api_request['query_params']['value']) == 1
            self.modules['left_eye'].color_loop = value
            self.modules['right_eye'].color_loop = value
        elif 'color' == operation:
            html_color = api_request['query_params']['value']
            value = tuple(int(html_color[i:i+2], 16) for i in (0, 2, 4))
            self.modules['left_eye'].color = value
            self.modules['right_eye'].color = value
            self.modules['left_eye'].all_pixels()
            self.modules['right_eye'].all_pixels()
        elif 'gill_control'  == operation:
            value = float(api_request['query_params']['value'])
            if value == -1:
                self.modules['gills'].setmode('normal')
            else:
                self.modules['gills'].setmode('color', value)

        elif operation == 'index': 
            return self.index()
        elif operation == 'calibrate_start':
            self.modules['cannon'].full_rotation()
        elif operation == 'calibrate_stop':
            self.modules['cannon'].calibration_finish()
        elif operation == 'calibrate_compass':
            self.modules['compass'].calibration()


def init_modules():
    right_eye = Eye(list(range(12)), (100, 0, 0))
    left_eye = Eye(list(range(12, 24)), (100, 0, 0))
    left_eye.eye_time = right_eye.eye_time # Pretty hacky but syncronizes the pulse
    # gills
    gills = Gills([Gill(list(range(24, 69)), color=(0, 0, 20), intensity=1.0)], [Gill(list(range(71, 131)), color=(0, 0, 20), intensity=1.0)])  # treat all as lefties for now...
    cannon = Cannon()

    return {'gills': gills, 'left_eye': left_eye, 'right_eye': right_eye, 'cannon': cannon, 'compass': Compass()}


async def main(modules):
    sound = SoundIntensity()

    while True:
        intensity = sound.next()

        modules['gills'].update_intensities(intensity)

        if not modules['cannon'].is_calibrating:
            compass_angle = modules['compass'].get_angle()
            modules['cannon'].rotate_to(compass_angle)

        ticks = ticks_ms()

        for module in modules.values():
            module.step(ticks)

        np.write()

        await asyncio.sleep_ms(1)


if __name__ == "__main__":
    modules = init_modules()
    api_handler = http_api_handler.Handler([([''], ApiHandler(modules))])
    loop = asyncio.get_event_loop()
    loop.create_task(main(modules))
    server = uhttpd.Server([('/api', api_handler)])
    server.run()
