import machine
import neopixel
from utime import ticks_diff, ticks_ms, ticks_add, sleep_ms
#  import uasyncio as asyncio
from micropython import const
import usocket
import socket
import uselect
import network
import sys
#  import webrepl

PIXEL_COUNT = const(60)
np = neopixel.NeoPixel(machine.Pin(5), PIXEL_COUNT)
STROBE_INTERVAL = const(40)
STROBE_TOTAL = const(5000)
PULSE_DURATION = const(100)
MAX_PULSE_LIGHT = const(150)
#  CHANGE = False
SERVER = "192.168.0.101"

class Module(object):
    def __init__(self, pixels, color=None, intensity=0.2):
        self.pixels = pixels
        self.color = color
        self.intensity = intensity
        self.mode = None
        self.change = False

    def all_pixels(self, onoff=True, color=None):
        #  global CHANGE
        if onoff:
            color = self._color_intensity(color)
        else:
            color = (0, 0, 0)
        for pixel in self.pixels:
            np[pixel] = color
        #  CHANGE = True
        self.change = True

    def _color_intensity(self, color=None):
        if color is None:
            return tuple(int(self.intensity * self.color[i]) for i in range(3))
        else:
            return tuple(int(self.intensity * color[i]) for i in range(3))


class Qualle(Module):

    def __init__(self, pixels, color, intensity=1):
        super(Qualle, self).__init__(pixels, color, intensity)
        self.all_pixels()
        self.mode = "pulse"
        self.pulse_rise = True
        self.last_tick = ticks_ms()
        self.strobo_on = True
        self.strobo_length = 1000
        self.strobo_start = ticks_ms()
        self.last_mode = "pulse"
        self.blink_tick = ticks_ms()
        self.ticks_diff_cached = ticks_diff

    def step(self, ticks):
        #  print("step")
        if abs(self.ticks_diff_cached(self.blink_tick, ticks)) < 200:
            return

        if self.mode == "pulse":
            if abs(self.ticks_diff_cached(self.last_tick, ticks)) < PULSE_DURATION:
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
            # print(self.color)
            self.all_pixels()

        elif self.mode == "strobo":
            if abs(self.ticks_diff_cached(self.strobo_start, ticks)) > self.strobo_length:
                self.mode = self.last_mode

            elif abs(self.ticks_diff_cached(self.last_tick, ticks)) > STROBE_INTERVAL:
                #  print(self.strobo_on)
                if self.strobo_on:
                    self.strobo_on = not self.strobo_on
                    self.all_pixels(True, (250,250,250))
                else:
                    self.strobo_on = not self.strobo_on
                    self.all_pixels(onoff=False)
                self.last_tick = ticks

    def blink(self):
        self.all_pixels(True, (255, 255, 0))
        self.blink_tick = ticks_ms()


    def set_mode(self, mode):
        if(self.mode != "strobo"):
            self.last_mode = self.mode
        self.mode = mode
        if mode == "strobo":
            self.strobo_start = ticks_ms()

def init_modules():
    qualle1 = Qualle(list(range(20)), (0, 0, MAX_PULSE_LIGHT))
    qualle2 = Qualle(list(range(20,40)), (0, 0, MAX_PULSE_LIGHT))
    qualle3 = Qualle(list(range(40,60)), (0, 0, MAX_PULSE_LIGHT))

    return {'1': qualle1, '2': qualle2, '3': qualle3}

class Receiver(object):
    def __init__(self, modules):
        self.poller = uselect.poll()
        self.sock = None
        self.is_connected = False
        self.np_write_cached = np.write
        self.modules = modules

    def connect_to_server(self):
        if not self.is_connected:
            # close old socket
            if self.sock is not None:
                print("closing existing socket")
                self.poller.unregister(self.sock)
                self.sock.close()

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                print("trying to connect to server")
                self.sock.connect((SERVER, 7654))
                self.is_connected = True
                print("successfully connected to server")
            except Exception as e:
                print(str(e))
            if self.is_connected:
                self.poller.register(self.sock, uselect.POLLIN)

    def receive(self, ticks):
        data = b''

        # poll non-blocking
        ret = self.poller.poll(0)
        if not ret:
            return

        obj, event = ret[0]
        if event == uselect.POLLHUP:
            print("POLLHUP")
            return
        elif event == uselect.POLLERR:
            print("POLLERR")
            return

        s = obj
        data = s.readline()
        print("Received at " + str(ticks) + ": " + str(data))

        # re-connect socket on connection loss
        if len(data) == 0: # This means the socket is dead
            print("Lost Connection")
            self.is_connected = False
            return

        # handle received packet
        if data.startswith(b'flash'):
            #  print("BLINK")
            try:
                id = int(data[6:8])
                if(id == 0):
                    for module in self.modules.values():
                        module.blink()
                #  elif(str(id) in modules.keys()):
                elif(self.modules.get(str(id), False)):
                    self.modules[str(id)].blink()
                #  np.write()
                self.np_write_cached()
            except Exception as e:
                print(e)

        elif data.startswith(b'set max_brightness'):
            brightness = int(data[19:22])
            print(str(brightness))
            print("set max_brightness")
            intensity = brightness / 255.0
            for module in self.modules.values():
                module.intensity = intensity

        elif data.startswith(b'kill'):
            sys.exit(0)

        elif data.startswith(b'set strobo_duration'):
            duration = int(data[20:23])
            print("Strobo duration set to", str(duration))
            for module in self.modules.values():
                module.strobo_length = duration*1000

        elif data.startswith(b'strobo'):
            #  print("Strobo")
            for module in self.modules.values():
                module.set_mode("strobo")

        elif data.startswith(b'ping'):
            pass

def main():
    modules = init_modules()

    ticks_ms_cached = ticks_ms
    np_write_cached = np.write
    change = False

    receiver = Receiver(modules)

    print("STARTING MAIN LOOP")

    while True:
        ticks = ticks_ms_cached()

        receiver.connect_to_server()
        receiver.receive(ticks)

        #  ticks = ticks_ms()

        for module in modules.values():
            module.step(ticks)
            if module.change:
                change = True
                module.change = False

        if change:
            #  np.write()
            #  print("write")
            np_write_cached()
        sleep_ms(1)
        #  await asyncio.sleep_ms(1)

if __name__ == "__main__":
    main()
