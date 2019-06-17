import machine
import neopixel
import time


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
    pixel_count = 80
    np = neopixel.NeoPixel(machine.Pin(13), pixel_count)

    while True:
        cycle(np, pixel_count)


if __name__ == "__main__":
    main()
