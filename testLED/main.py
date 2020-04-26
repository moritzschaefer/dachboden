
import machine
import neopixel
import utime
import socket

n = 10
p = 16

np = neopixel.NeoPixel(machine.Pin(p), n)

np[0] = (255, 0, 0)
np[3] = (125, 204, 223)
np[7] = (120, 153, 23)
np[10] = (255, 0, 153)

#for i in range(0,100):
#    np[i] = (100,100,100)


np.write()
