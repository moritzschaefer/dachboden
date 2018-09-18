from machine import SPI, Pin
import time
import utime
import socket
import array


class ShiftRegister:
    # On ESP8266 (NodeMCU V3), use MOSI (for DI) and SCLK (for CI)
    def __init__(self, rclk, initial=b'\x00\x00\x00'):
        self.spi = SPI(1, baudrate=10000000, polarity=0, phase=0)
        self.rclk = rclk
        self.data = bytearray(initial)
        # self.oe = oe
        # TODO make sure these PINs are connected to VCC/Ground respectively on the 74HC595
        # self.oe.value(0) # output enable
        # self.clr.value(1) # don't reset shift regs

    # def clear(self):
    #     self.clr.value(0) # clear shift regs
    #     self.rclk.value(1) # latch data to output
    #     self.rclk.value(0)
    #     self.clr.value(1)

    def set_all(self, buf):
        ''' buf needs to be a byte string'''
        self.data = bytearray(buf)
        while len(self.data) < 3:
            self.data.append(0)
        self._shift()

    def set_one(self, number, value):
        try:
            if value:
                self.data[number // 8] = self.data[number // 8] | (1 << (number % 8))
            else:
                self.data[number // 8] = self.data[number //
                                                  8] & (0xff ^ (1 << (number % 8)))
        except IndexError:
            print('channel (number) too high')
        else:
            self._shift()

    def _shift(self):
        self.spi.write(self.data)
        self.rclk.value(1)  # latch data to output
        self.rclk.value(0)



# 1   8  14  21
#   5  12  18
# 2   9  15  22
#   6  13  19
# 3  10  16  23
#   7  --  20
# 4  11  17  24


def callback(sr, universe, channel, value):
    print((universe, channel, value))
    sr.set_one(channel, value)


def main():
    # rclk: D1=GPIO5 Pin
    sr = ShiftRegister(Pin(5, Pin.OUT))

    t0 = utime.ticks_ms()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('0.0.0.0', 9000)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)
    sock.settimeout(0.1)
    i = 0
    while True:
        try:
            data, _ = sock.recvfrom(64)
        except OSError:  # timeout!!
            t = (utime.ticks_ms() - t0) / 100000
            sr.set_all(i.to_bytes(2, 'little')[:3])
            time.sleep_ms(300)
            print('Set shift register to {}'.format(i))
            i += 1
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
            callback(sr, universe, channel, value)
            data, _ = sock.recvfrom(64)
    finally:
        sock.close()


if __name__ == '__main__':
    main()
