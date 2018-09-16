from bibliopixel.animation import BaseStripAnim

class MatrixAnimator(BaseStripAnim):
    def __init__(self, led, lines, reverse=True): # , on_time, black_time):
        super(MatrixAnimator, self).__init__(led)
        self._lines = lines
        self._reverse = reverse

    def step(self, amt=1):
        """ TODO, this should maybe playback back and forth """
        # if self._step % 2 == 0:
            # colors = [(0,0,0)] * self._led.numLEDs
        # else:
            # colors = self._lines[(self._step / 2) % len(self._lines)]

        # check if displaying should be forward or backwards!

        if (self._step / len(self._lines)) % 2 == 0:
            # display forward
            colors = self._lines[(self._step % len(self._lines))]
        else:
            # display backwards
            colors = self._lines[len(self._lines)-(self._step % len(self._lines))-1]
        if self._reverse:
            colors = list(reversed(colors))
            

        for i in range(self._led.numLEDs):
            self._led.set(i, colors[i])

        self._step += amt




