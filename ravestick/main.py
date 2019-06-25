import math
import machine
import neopixel
from utime import ticks_diff, ticks_ms, ticks_add, sleep_ms
import http_api_handler
import uhttpd
import uasyncio as asyncio

#Auge1 0-11 Auge2 12-23 Kiemen1 24-x Kiemen2 x+1-y Inner y+1-max

PIXEL_COUNT = 180
np = neopixel.NeoPixel(machine.Pin(13), PIXEL_COUNT)
SAMPLE_COUNT = 170  # TODO tweak
WINDOW_LENGTH = 20  # TODO tweak
WINDOW_WEIGHTS = [0.8**i for i in range(WINDOW_LENGTH)]
WEIGHT_SUM = sum(WINDOW_WEIGHTS)
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
        self.long_term_std = 0.5
        self.buffer = [0] * WINDOW_LENGTH  #  (for smoothing)
        self.index = 0
        self.adc = machine.ADC(machine.Pin(33))
        self.adc.atten(machine.ADC.ATTN_11DB)  # 3,6V input
        self.adc.width(machine.ADC.WIDTH_12BIT)  # 3,6V input
        self.mean_voltage = 1000

    def current_average(self):
        summed = 0
        weight = 1.0
        for i, weight in zip((i for j in (range(self.index, -1, -1), range(WINDOW_LENGTH - 1, self.index, -1)) for i in j), WINDOW_WEIGHTS):
            summed += weight * self.buffer[i]

        return summed / (WEIGHT_SUM)


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
            sum(self.buffer) / len(self.buffer)

            self.long_term_buffer[self.ltb_index] = sum(self.buffer) / len(self.buffer)
            self.ltb_index = (self.ltb_index + 1) % len(self.long_term_buffer)
            self.long_term_mean = sum(self.long_term_buffer) / len(self.long_term_buffer)
            self.long_term_std = 0
            for v in self.long_term_buffer:
                self.long_term_std += (v - self.long_term_mean)**2
            self.long_term_std = math.sqrt(self.long_term_std / (len(self.long_term_buffer) - 1))

        # mi, ma = min(self.long_term_buffer), max(self.long_term_buffer)

        # val =  min(1.0, max(0.00, (cur_val - mi) / max(0.01, ma - mi)))
        # print(mi, ma, val)
        # return val**3
        # print((cur_val - self.long_term_mean) / self.long_term_std)

        intensity = self.long_term_std + (cur_val - self.long_term_mean) / self.long_term_std
        # print(intensity)
        return min(1.0, max(0.0, intensity))


class Gills:
    def __init__(self, lefts, rights):
        self.lefts = lefts
        self.rights = rights
        self.mode = 'normal'

    def step(self, ticks):
        pass

    def all_pixels(self, onoff=True):
        for gill in self.lefts + self.rights:
            gill.all_pixels(onoff)

    def update_intensities(self, intensity):
        if mode == 'normal':
            for gill in self.lefts + self.rights:
                gill.intensity = intensity
            # print(intensity)
            self.all_pixels()
        else:
            pass

    def set(self, mode):
        if mode != 'normal':
            self.update_intensities(mode)
        self.mode = None


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

    def blink(self):
        self.blink_end = ticks_add(ticks_ms(), self.blink_duration)
        self.all_pixels(False)

    def step(self, ticks):
        if not self.color_loop:
            if self.blink_end is not None and ticks_diff(self.blink_end, ticks) < 0:
                self.all_pixels(True)
                self.blink_end = None
        else:
            # color loop code!!!
            pass  # TODO marco JUST DO IT


class ApiHandler:
    def __init__(self, modules):
        self.modules = modules

    def index(self):
        return '''
        <html><head><title>MantaControl</title></head>
        <body>
        <button onclick="call('/api/left_eye')">Zwinker Links</button>
        <button onclick="call('/api/right_eye')">Zwinker Rechts</button>
        <input type="color" id="color"/>
        <label><input type="checkbox" id="color_loop" onclick="handleClick(this)"/>Color loop</label>
        <label><input type="checkbox" id="music" onclick="handleMusic(this)"/>Music</label>
        <input type="range" min=0 max=1 step=0.02 id="range"/>
        <p id="result">Press a button</p>
        <script type="text/javascript">
        var range = document.getElementById("range");
        range.addEventListener("change", function(event) {
        if(document.getElementById("music").value)
            call('gill_control', event.target.value);

        }, false);
        function handleClick(cb) {
        call('color_loop', cb.checked);
        }
        function handleMusic(cb) {
        if(cb.checked)
            call('gill_control', -1);
        else
            call('gill_control', document.getElementById("range").value);
        }
        function call(path, val) {
        var xhttp = new XMLHttpRequest();
        document.getElementById("result").innerHTML = "calling";
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
            document.getElementById("result").innerHTML = "done";
            }
        };
        if(val) {
        path = path + "?value=" + val;
        }
        xhttp.open("GET", path, true);
        xhttp.send();
        }
        var cp = document.getElementById('color');
        cp.addEventListener("change", function(event) {
        call('color', event.target.value);
        }, false);

        </script>
        </body>
        </html>
        '''

    def get(self, api_request):
        print(api_request)
        if left_eye:
            self.modules['left_eye'].blink()
        if right_eye:
            self.modules['right_eye'].blink()
        if color_loop:
            value = False/True  # TODO
            self.modules['left_eye'].color_loop = value
            self.modules['right_eye'].color_loop = value
        if color:
            # TODO parse value !! (hex string to (1, 2, 3))
            self.modules['left_eye'].color = value
            self.modules['right_eye'].color = value
            self.modules['left_eye'].all_pixels()
            self.modules['right_eye'].all_pixels()

        if gill_control:
            if value < 0:
                self.modules.gills.set('normal')
            else:
                self.modules.gills.set(value)

        return {'foo': 'bar'}

def init_modules():
    left_eye = Eye(list(range(12)), (100, 0, 0))
    right_eye = Eye(list(range(12, 24)), (100, 0, 0))
    # gills
    gills = Gills([Gill(list(range(24, 69)), color=(0, 0, 20), intensity=1.0)], [Gill(list(range(71, 131)), color=(0, 0, 20), intensity=1.0)])  # treat all as lefties for now...

    return {'gills': gills, 'left_eye': left_eye, 'right_eye': right_eye}


async def main(modules):
    sound = SoundIntensity()
    print('im here')


    while True:
        intensity = sound.next()

        modules['gills'].update_intensities(intensity)

        ticks = ticks_ms()

        for module in modules.values():
            module.step(ticks)

        np.write()
        await asyncio.sleep_ms(1)


if __name__ == "__main__":
    modules = init_modules()
    api_handler = http_api_handler.Handler([(['left_eye', 'right_eye', 'color_loop', 'color', 'gill_control'], ApiHandler(modules))])
    loop = asyncio.get_event_loop()
    loop.create_task(main(modules))
    server = uhttpd.Server([('/api', api_handler)])
    server.run()
