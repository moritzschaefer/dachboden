import machine
import neopixel
from time import sleep


np = neopixel.NeoPixel(machine.Pin(13), 12+12)
np_rgbw = neopixel.NeoPixel(machine.Pin(17), 7, bpp=4)

def main():
    while True:
        for i in range(24):
            np[i] = (int(round(51/5)), int(round(255/5)), int(round(255/5)))
        for i in range(0, 7):
            np_rgbw[i] = (50, 50, 50, 50)
        np.write()
        np_rgbw.write()
        sleep(0.07)

#strobomodus
        for i in range(24):
            np[i] = (int(round(51/5)), int(round(255/5)), int(round(255/5)))
        for i in range(0, 7):
            np_rgbw[i] = (0, 0, 0, 0)
        np.write()
        np_rgbw.write()
        sleep(0.07)



if __name__ == "__main__":
    main()
