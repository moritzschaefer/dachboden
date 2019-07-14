import math
import machine
import neopixel
from utime import ticks_diff, ticks_ms, ticks_add, sleep_ms
import http_api_handler
import uhttpd
import uasyncio as asyncio
from ApiHandler import ApiHandler
from math import sin
#Auge1 0-11 Auge2 12-23 Kiemen1 24-x Kiemen2 x+1-y Inner y+1-max

PIXEL_COUNT = 20
np = neopixel.NeoPixel(machine.Pin(5), PIXEL_COUNT)
STROBE_LENGTH = 10
STROBE_TOTAL = 5000
PULSE_DURATION = 10000
MAX_PULSE_LIGHT = 100
CHANGE = False

class Module(object):
    def __init__(self, pixels, color=None, intensity=1.0):
        self.pixels = pixels
        self.color = color
        self.intensity = intensity

    def all_pixels(self, onoff=True):
        global CHANGE
        if onoff:
            color = self._color_intensity()
        else:
            color = (0, 0, 0)
        for pixel in self.pixels:
            np[pixel] = color
        CHANGE = True
    def _color_intensity(self):
        return tuple(int(self.intensity * self.color[i]) for i in range(3))


class Qualle(Module):

    def __init__(self, pixels, color, intensity=1):
        super(Qualle, self).__init__(pixels, color, intensity)
        self.all_pixels()
        self.mode = "pulse"
        self.pulse_rise = True
        self.last_tick = ticks_ms()
    def step(self, ticks):
        if self.mode == "pulse":
            if abs(ticks_diff(self.last_tick, ticks)) < PULSE_DURATION/MAX_PULSE_LIGHT:
                return
            self.last_tick = ticks
            if self.pulse_rise:
                if self.color[2] >= MAX_PULSE_LIGHT:
                    self.pulse_rise = False
                else:
                    self.color = (0, max(self.color[1] - 1, 0), self.color[2] + 1)
            else:
                if (self.color[2] <=0):
                    self.pulse_rise = True
                else:
                    self.color = (0, self.color[1] + 1, max(self.color[2] - 1, 0))
            print(self.color)
            self.all_pixels()
def init_modules():
    qualle =Qualle(list(range(20)), (0, 0, MAX_PULSE_LIGHT))

    return {'Main': qualle}


async def main(modules):
    global CHANGE
    while True:


        ticks = ticks_ms()

        for module in modules.values():
            module.step(ticks)

        if CHANGE:
            np.write()
            CHANGE = False
        #sleep_ms(20)
        await asyncio.sleep_ms(1)


if __name__ == "__main__":
    modules = init_modules()
    #main(modules)
    api_handler = http_api_handler.Handler([([''], ApiHandler(modules))])
    loop = asyncio.get_event_loop()
    loop.create_task(main(modules))
    server = uhttpd.Server([('/api', api_handler)])
    server.run()