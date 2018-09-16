import sys
import time

from bibliopixel import LEDStrip
from bibliopixel.drivers.driver_base import ChannelOrder
from bibliopixel.drivers.LPD8806 import DriverLPD8806

from loader import load
from matrix_animator import MatrixAnimator


FILENAME = 'first.bw'

driver = DriverLPD8806(num=32, c_order=ChannelOrder.BRG)
strip = LEDStrip(driver)


def main(filename):
    
    animator = MatrixAnimator(strip, load(filename), False)
    animator.run(threaded=True)
    return animator

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main(FILENAME)
    else:
        main(sys.argv[1])

    print('Press enter to finish the program')
    raw_input()
