import ubinascii
import machine
import socket
import array
import micropython
import neopixel

# LED sripe has 27 RGB LEDs
leds = neopixel.NeoPixel(machine.Pin(5, machine.Pin.OUT), 27)


def main():
    #default light on
    for i in range(27):
        leds[i] = (256,150,150)
    leds.write()
    osc_listen(callback)


def osc_listen(callback):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('0.0.0.0', 9000)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)
    try:
        while True:
            data, _ = sock.recvfrom(64)
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
    finally:
        sock.close()


def callback(universe, channel, value):

    tmp = list(leds[channel//3])
    tmp[channel % 3] = int(value*255)
    leds[channel // 3] = tuple(tmp)

    leds.write()


if __name__ == '__main__':
    main()
