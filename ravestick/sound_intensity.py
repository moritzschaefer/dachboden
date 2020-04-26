import math

import machine

SAMPLE_COUNT = 170  # TODO tweak
WINDOW_LENGTH = 20  # TODO tweak
WINDOW_WEIGHTS = [0.8**i for i in range(WINDOW_LENGTH)]
WEIGHT_SUM = sum(WINDOW_WEIGHTS)
NORMALIZER_LENGTH = 20  # TODO tweak


class SoundIntensity:
    '''
    Map microphone input to intensities
    TODO maybe add weighted (new intensities are more important)
    '''
    def __init__(self):
        self.long_term_buffer = [0.1] * NORMALIZER_LENGTH
        self.ltb_index = 0
        self.long_term_mean = 0.1
        self.long_term_std = 0.5
        self.buffer = [0] * WINDOW_LENGTH  # (for smoothing)
        self.index = 0
        self.adc = machine.ADC(machine.Pin(32))  # TODO new PIN
        self.adc.atten(machine.ADC.ATTN_11DB)  # 3,6V input
        self.adc.width(machine.ADC.WIDTH_12BIT)  # 3,6V input
        self.mean_voltage = 1000

    def current_average(self):
        summed = 0
        weight = 1.0
        for i, weight in zip((i for j in (range(self.index, -1, -1), range(WINDOW_LENGTH - 1, self.index, -1)) for i in j), WINDOW_WEIGHTS):
            summed += weight * self.buffer[i]

        return summed / (WEIGHT_SUM)

    def _new_value(self, val):
        '''
        :val: float from 0 to 1
        '''
        self.buffer[self.index] = val
        self.index = (self.index + 1) % len(self.buffer)

    def next(self):
        power = 0
        mean = 0
        for i in range(SAMPLE_COUNT):
            a = self.adc.read()
            power += abs(a - self.mean_voltage)
            mean += a

        self._new_value(power / max(1, SAMPLE_COUNT * self.mean_voltage))
        cur_val = self.current_average()
        self.mean_voltage = mean / SAMPLE_COUNT

        # add to long term average
        if self.index == 0:
            sum(self.buffer) / len(self.buffer)

            self.long_term_buffer[self.ltb_index] = sum(self.buffer) / len(self.buffer)
            self.ltb_index = (self.ltb_index + 1) % len(self.long_term_buffer)
            self.long_term_mean = sum(self.long_term_buffer) / len(self.long_term_buffer)
            self.long_term_std = 0
            for v in self.long_term_buffer:
                self.long_term_std += (v - self.long_term_mean)**2
            self.long_term_std = math.sqrt(self.long_term_std / (len(self.long_term_buffer) - 1))

        # mi, ma = min(self.long_term_buffer), max(self.long_term_buffer)

        # val =  min(1.0, max(0.00, (cur_val - mi) / max(0.01, ma - mi)))
        # print(mi, ma, val)
        # return val**3
        # print((cur_val - self.long_term_mean) / self.long_term_std)

        intensity = self.long_term_std + (cur_val - self.long_term_mean) / max(1, self.long_term_std)
        # print(intensity)
        return min(1.0, max(0.0, intensity))
