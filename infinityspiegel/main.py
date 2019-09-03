import machine, neopixel, time
import utime #for strobo

PIN = 34
NUM_PIXEL = 108
INTENSITY = 40

RED = (16, 0, 0)
GREEN = (1, 8, 0)
YELLOW = (15, 15, 0)
WHITE = (50, 50, 50)
BLACK = (0, 0, 0)

np = neopixel.NeoPixel(machine.Pin(PIN), NUM_PIXEL)


for i in range(NUM_PIXEL):
    np[i] = (16,0,0)
np.write()