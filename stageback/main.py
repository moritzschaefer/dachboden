from time import sleep

from shiftpi.shiftpi import setRegisters, HIGH, LOW
from machine import SPI, Pin

class ShiftRegister:
    # On ESP8266 (NodeMCU V3), use MOSI (for DI) and SCLK (for CI)
    def __init__(self, rclk):
        self.spi = SPI(1, baudrate=100000, polarity=0, phase=0)
        self.rclk = rclk
        # self.oe = oe
        # TODO make sure these PINs are connected to VCC/Ground respectively on the 74HC595
        # self.oe.value(0) # output enable
        # self.clr.value(1) # don't reset shift regs

    # def clear(self):
    #     self.clr.value(0) # clear shift regs
    #     self.rclk.value(1) # latch data to output
    #     self.rclk.value(0)
    #     self.clr.value(1)


    def shift(self, buf):
        ''' buf needs to be a byte string (or array)'''
        self.spi.write(buf)
        self.rclk.value(1)  # latch data to output
        self.rclk.value(0)

# rclk: SD2=GPIO9 Pin
sr = ShiftRegister(Pin(9, Pin.OUT))

# 1   8  14  21
#   5  12  18
# 2   9  15  22
#   6  13  19
# 3  10  16  23
#   7  --  20
# 4  11  17  24

def expand(l):
    r = [1] * 24

    for pin in l:
        r[pin-1] = 0
    return r


def first():
    outer = [1,1,1,1,0,0,0,1,1,1,1,0,0,1,1,1,1,0,0,0,1,1,1,1]
    inner = [0,0,0,0,1,1,1,0,0,0,0,1,1,0,0,0,0,1,1,1,0,0,0,0]

    setRegisters(outer)
    sleep(0.3)

    setRegisters(inner)
    sleep(0.3)


def second():
    setRegisters(expand((1,8,14,21)))
    sleep(0.3)
    setRegisters(expand((5,12,18)))
    sleep(0.3)
    setRegisters(expand((2,9,15,22)))
    sleep(0.3)
    setRegisters(expand((6,13,19)))
    sleep(0.3)
    setRegisters(expand((3,10,16,23)))
    sleep(0.3)
    setRegisters(expand((7,20)))
    sleep(0.3)
    setRegisters(expand((4,11,17,24)))
    sleep(0.3)


def main():
    while True:
        for _ in range(100):
            first()

        for _ in range(100):
            second()


if __name__ == '__main__':
    main()
