import machine
import neopixel
import utime

import uasyncio as asyncio
import uos

def rand():
    return int.from_bytes(uos.urandom(4), 'little')


def randint(a, b):
    return (rand() % (b - a)) + a


DATA_PIN = 4

#TOUCHPINS 0,2,4,12,13,14,15,27,32,33
PINS = [13,14,32,33]
PINBLACK = 13
PINMODE = 32
THRESHHOLD = 150
PIXELS = 102
MAX_ROTATIONS = 20
INTENSITY = 0.8

class SchlauchHero:
    colors=[(200,0,0), (0,200,0), (0,0,200), (200,0,200), (200,200,200)]
    level_speed = [1000, 500, 250, 100, 50, 25, 10]
    width = 10
    light = 0
    def __init__(self):
        self.time = utime.ticks_ms()
        self.button_time = utime.ticks_ms()
        self.int_board = [4 for i in range(PIXELS)]
        self.board = [self.colors[i] for i in self.int_board]
        self.sender = Sender()
        self.sender.send(self.board)
        self.restart()

    def set_board(self):
        self.board = [self.colors[i] for i in self.int_board]

    def get_lights(self):
        return self.board

    def restart(self):
        self.mode = "live"
        self.time_progress = 0
        self.life = 3
        self.score = 0
        self.cur_generation_width = 0
        self.cur_generation_color = 4

    def set_color(self, player, color):
        self.player_colors[player] = tuple([int(x * INTENSITY) for x in color])
        self.board = [self.player_colors[player] for x in self.board]
        self.sender.send(self.board)

    def pause(self):
        self.mode = "pause"

    def pause_or_play(self):
        # Not used
        if self.mode == "pause":
            self.start()
        else:
            self.pause()

    def start(self):
        self.time = utime.ticks_ms()
        self.time_progress = 0
        self.mode = "live"
        self.sender.send(self.board)


    def check_correct(self, command):
        # Check if the correct Button is pressed

        pressed = [i for i in range(4) if command[i]]
        if len(pressed) == 1:
            self.button_time = utime.ticks_ms()
            # Single Button press
            if self.int_board[self.light] == pressed[0]:
                # Correct
                self.int_board[self.light] = 4 # Some reward
                self.score += 1
            else:
                # Wrong
                self.life -= 1
                if self.life <= 0:
                    self.restart()

    def move_color(self):
        # Move the light, randomly spawn a new color
        for i in range(PIXELS-1):
            self.int_board[i] = self.int_board[i+1]
            self.board[i] = self.board[i+1]

        if self.cur_generation_width <= 0:
            self.cur_generation_color = randint(0,4)
            self.cur_generation_width = self.width

        self.int_board[PIXELS-1] = self.cur_generation_color
        self.board[PIXELS-1] = self.colors[self.cur_generation_color]
        self.cur_generation_width -= 1



    def step(self, command):
        if utime.ticks_ms() - self.button_time > 50:
            self.check_correct(command)
        # Check if time is ready to move the light
        if utime.ticks_ms() - self.time > self.level_speed[max(self.score//10,len(self.level_speed)+1)]:
            self.time = utime.ticks_ms()
            self.move_color()
            self.sender.send(self.board)


class Sender():
    def __init__(self):
        self.neop = neopixel.NeoPixel(machine.Pin(DATA_PIN), PIXELS)

    def send(self, pixel_values):
        for i in range(PIXELS):
            self.neop[i] = pixel_values[i]
        self.neop.write()

class OnboardControl():
    def __init__(self):
        self.pins = [machine.TouchPad(machine.Pin(pin)) for pin in PINS]

    def step(self):
        responses = [self.pins[i].read() < THRESHHOLD for i in range(4)]

        return responses

async def main(hero, controller):

    while True:
        command = controller.step()
        #print(TouchCommand)
        hero.step(command)
        await asyncio.sleep_ms(5)



if __name__ == "__main__":
    hero = SchlauchHero()
    controller = OnboardControl()
    loop = asyncio.get_event_loop()
    loop.create_task(main(hero, controller))

