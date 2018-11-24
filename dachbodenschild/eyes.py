import utime
from main import Sender


PIXELS_EYE = 12
PIN_EYE = 5
class Eyes:

    eye_step = 50
    eye_width = 3
    def __init__(self):

        self.eyes = [(0,0,0) for i in range(2*PIXELS_EYE)]
        self.sender_eyes = Sender(PIN_EYE, 2*PIXELS_EYE)
        self.eye_pos = 0
        self.eye_time = utime.ticks_ms()
        self.eye_rotatations = 0
        self.eye_mode = 0

    def circling_eyes(self, color):

        eye_percentage = abs(utime.ticks_diff(self.eye_time, utime.ticks_ms())) / float(self.eye_step)
        if (eye_percentage >= 1):
            self.eye_time = utime.ticks_ms()
            self.eye_pos = (self.eye_pos + 1) % PIXELS_EYE
        self.eyes = [(0, 0, 0) for i in range(PIXELS_EYE * 2)]
        for i in range(self.eye_width):

            if (i == 0):
                self.eyes[i + self.eye_pos] = (
                    int((1 - eye_percentage) * color[0]), int((1 - eye_percentage) * color[1]),
                    int((1 - eye_percentage) * color[2]))
                self.eyes[i + self.eye_pos + 12] = (
                    int((1 - eye_percentage) * color[0]), int((1 - eye_percentage) * color[1]),
                    int((1 - eye_percentage) * color[2]))
            elif (i == self.eye_width - 1):
                self.eyes[(i + self.eye_pos) % PIXELS_EYE] = (
                int(eye_percentage * color[0]), int(eye_percentage * color[1]),
                int(eye_percentage * color[2]))
                self.eyes[((i + self.eye_pos) % PIXELS_EYE) + 12] = (
                    int(eye_percentage * color[0]), int(eye_percentage * color[1]),
                    int(eye_percentage * color[2]))
            else:
                self.eyes[(i + self.eye_pos) % PIXELS_EYE] = color
                self.eyes[((i + self.eye_pos) % PIXELS_EYE) + 12] = color
        self.sender_eyes.send(self.eyes)