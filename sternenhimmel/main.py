'''
This script glows by default and once an OSC packet comes in, it only shows what is sent by OSC
'''
import machine
import neopixel
from math import sin
import utime
import uos
import socket
import array

# Channels: 150

# 0,1,2 RGB Pixel 0
# 3,4,5 RGB Pixel 1
# ...


PIXELS = 50

np = neopixel.NeoPixel(machine.Pin(2), PIXELS)

def rand():
    return int.from_bytes(uos.urandom(1), 'little')


class Star:
    def __init__(self):
        self.color = [int(rand()/1.5), int(rand()), int(rand()/2)]
        self.interval = 50 + (rand() % 50)
        print(self.interval)

    def step(self, t):
        intensity = (sin(self.interval * t) / 2.0) + 0.5

        return [int(0.5 * intensity * v) for v in self.color]


stars = [Star() for _ in range(PIXELS)]

def main():
    t0 = utime.ticks_ms()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('0.0.0.0', 9000)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)
    sock.settimeout(0.1)

    # do the default stuff until we get an OSC call!
    while True:
        try:
            data, _ = sock.recvfrom(64)
        except OSError:  # timeout!!
            t = (utime.ticks_ms() - t0) / 100000
            for i in range(PIXELS):
                np[i] = stars[i].step(t)
            np.write()
        else:
            break  # go out of the for loop!

    sock.settimeout(None)

    try:
        while True:
            universe_end = data.find(b'/', 1)
            universe = int(data[1:universe_end])
            channel_end = data.find(b'\x00')
            channel = int(data[universe_end+5:channel_end])
            value = bytearray()
            value.append(data[-1])
            value.append(data[-2])
            value.append(data[-3])
            value.append(data[-4])
            value = array.array('f', value)[0]
            callback(universe, channel, value)
            data, _ = sock.recvfrom(64)
    finally:
        sock.close()


def callback(universe, channel, value):
    # print((universe, channel, value))
    tmp = list(np[channel//3])
    tmp[channel%3] = int(value*255)
    np[channel//3] = tuple(tmp)
    np.write()

if __name__ == "__main__":
    main()
