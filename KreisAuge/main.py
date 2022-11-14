import machine, neopixel
import math
from utime import ticks_diff, ticks_ms, ticks_add, sleep_ms
import urandom

PIN = 4
NUM_PIXEL = 250
MAX_ITENSITY = 190
V_MIN = -15
V_MAX = 15
MAX_ZEIGER = 125
MIN_ZEIGER = 1


def randint(min, max):
    span = max - min + 1
    div = 0x3fffffff // span
    offset = urandom.getrandbits(30) // div
    val = min + offset
    return val

def test_pin(pin):
    x = neopixel.NeoPixel(machine.Pin(pin), 100)
    for i in range(100):
        x[i] = (100,100,0)
    x.write()

class KreisAuge:
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
        self.reset_zeiger()
        #self.mass_bias = randint(1,100)/100.
    def reset_zeiger(self, n = 20):
        self.n = n
        for i in range(NUM_PIXEL):
            self.np[i] = (0, 0, 0)
        self.zeiger_pos = [i * NUM_PIXEL // self.n for i in range(self.n)]
        self.zeiger_v = [randint(V_MIN, V_MAX) for _ in range(self.n)]
        for i in range(len(self.zeiger_v)):
            if self.zeiger_v[i] == 0:
                self.zeiger_v[i] = 1
        self.zeiger_color = [hsv_to_rgb(randint(0,360), 1, 1) for _i in range(self.n)]
        self.zeiger_counter = [0 for _ in range(self.n)]

        for i in range(self.n):
            self.np[self.zeiger_pos[i]] = self.zeiger_color[i]
            self.np.write()
            sleep_ms(20)

    def step(self, ticks):
        if abs(ticks - self.last_step) >600000:
            self.reset_zeiger(randint(MIN_ZEIGER,MAX_ZEIGER))
            self.last_step = ticks_ms()
        for i in range(self.n):
            if self.zeiger_v[i] == 0:
                #Why can a pixel have 0 Velocity?
                continue
            self.zeiger_counter[i] = (self.zeiger_counter[i] + 1 ) % abs(self.zeiger_v[i])
            if self.zeiger_counter[i] == 0:
                self.zeiger_pos[i] = (self.zeiger_pos[i] + 1) % NUM_PIXEL if self.zeiger_v[i] > 0 else (self.zeiger_pos[i] - 1) % NUM_PIXEL
        for i in range(NUM_PIXEL):
            self.np[i] = (0,0,0)

        i = 0
        mass_bias = math.cos(ticks/30000)+1
        while i < self.n:
            if i >= len(self.zeiger_pos):
                print("Should never happen, but who knows")
                break
            if sum(self.np[self.zeiger_pos[i]]) > 0:
                if randint(0,10) >= 8: #Check, if we want to add or remove a Zeiger
                    urandom_event = randint(MIN_ZEIGER, MAX_ZEIGER)
                    if urandom_event *mass_bias > self.n: #Adding
                        self.add_zeiger(pos=self.zeiger_pos[i])
                        self.np[self.zeiger_pos[i]] = (MAX_ITENSITY,MAX_ITENSITY, MAX_ITENSITY)
                    elif urandom_event < self.n: # Removing
                        self.np[self.zeiger_pos[i]] = (0, 0, 0)
                        self.remove_zeiger(i)
                        continue
            else:
                self.np[self.zeiger_pos[i]] = self.zeiger_color[i]
            i += 1
        self.np.write()

    def add_zeiger(self, pos=None, v=None):
        if len(self.zeiger_pos) < MAX_ZEIGER:
            if pos:
                self.zeiger_pos.append(pos)
            else:
                self.zeiger_pos.append(randint(0, NUM_PIXEL))
            if v:
                self.zeiger_v.append(v)
            else:
                new_v = randint(V_MIN,V_MAX)
                if new_v == 0:
                    new_v = 1
                self.zeiger_v.append(new_v)
            self.zeiger_color.append(hsv_to_rgb(randint(0,360), 1, 1))
            self.zeiger_counter.append(0)
            self.n = len(self.zeiger_pos)

    def remove_zeiger(self, idx=-1):
        if len(self.zeiger_pos) > MIN_ZEIGER:
            if idx < 0 or idx > len(self.zeiger_pos):
                idx = randint(0,len(self.zeiger_pos))
            self.zeiger_pos.pop(idx)
            self.zeiger_v.pop(idx)
            self.zeiger_color.pop(idx)
            self.zeiger_counter.pop(idx)
            self.n = len(self.zeiger_pos)

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


def main(ka):

    while True:

        ticks = ticks_ms()
        sleep_ms(20)
        ka.step(ticks)


if __name__ == "__main__":
    ka = KreisAuge()
    main(ka)
