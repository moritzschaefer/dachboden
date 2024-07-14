import machine
import neopixel
import utime
import uasyncio as asyncio
import uos
import tm1637

def rand():
    return int.from_bytes(uos.urandom(4), 'little')

def randint(a, b):
    return (rand() % (b - a)) + a

DATA_PIN = 4
#TOUCHPINS 0,2,4,12,13,14,15,27,32,33
LED_PINS = [13]
INPUT_PINS = [5, 16,17,18]
PINS_SETTING = [21,22,23,25]
LIFE_PINS = [3, 4]
SCORE_PINS = [5, 6]
THRESHHOLD = 150
PIXELS = 5*60

class SchlauchHero:
    colors=[(200,0,0), (0,200,0), (0,0,200), (200,0,200), (200,200,200), (0,0,0)]
    level_speed = [1000, 500, 250, 100, 50, 25, 10]
    width = 10
    light = 0
    def __init__(self):
        self.time = utime.ticks_ms()
        self.button_time = utime.ticks_ms()
        self.int_board = [4 for i in range(PIXELS)]
        self.board = [self.colors[i] for i in self.int_board]
        self.sender = Sender()
        self.score_monitor = tm1637.TM1637(clk=machine.Pin(SCORE_PINS[0]), dio=machine.Pin(SCORE_PINS[1]))
        self.life_monitor = tm1637.TM1637(clk=machine.Pin(LIFE_PINS[0]), dio=machine.Pin(LIFE_PINS[1]))
        self.sender.send(self.board)
        self.restart()
        self.current_colors = [0, 1, 2, 3]

    def update_score(self):
        self.score_monitor.number(self.score)

    def update_life(self):
        self.life_monitor.number(self.life)

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
        self.update_score()
        self.update_life()

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
                self.update_score()
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
            if len(self.current_colors) == 0:
                self.cur_generation_color = randint(0,4)
            self.cur_generation_color = self.current_colors[randint(0,len(self.current_colors))]
            self.cur_generation_width = self.width

        self.int_board[PIXELS-1] = self.cur_generation_color
        self.board[PIXELS-1] = self.colors[self.cur_generation_color]
        self.cur_generation_width -= 1

    def send_color(self, command):
        for i in range(1, PIXELS):
            self.int_board[i] = self.int_board[i-1]
            self.board[i] = self.board[i-1]
        pressed = [i for i in range(4) if command[i]]
        if len(pressed) == 1:
            self.int_board[0] = pressed[0]
            self.board[0] = self.colors[pressed[0]]

    def step(self, command):
        if self.mode =="sending":
            self.send_color(command)
            return

        if utime.ticks_ms() - self.button_time > 50:
            self.check_correct(command)
        # Check if time is ready to move the light
        if utime.ticks_ms() - self.time > self.level_speed[max(self.score//10,len(self.level_speed)+1)]:
            self.time = utime.ticks_ms()
            self.move_color()
            self.sender.send(self.board)

    def set_colors(self, colors):
        self.current_colors = colors
        if len(self.current_colors) == 0:
            self.mode = "sending"
        else:
            self.mode = "live"

class Sender:
    def __init__(self):
        self.neop = neopixel.NeoPixel(machine.Pin(DATA_PIN), PIXELS)

    def send(self, pixel_values):
        for i in range(PIXELS):
            self.neop[i] = pixel_values[i]
        self.neop.write()

class OnboardControl:
    def __init__(self):
        self.pins = [machine.Pin(pin, machine.Pin.IN) for pin in INPUT_PINS]
        self.responses = [False] * len(INPUT_PINS)
        for pin in self.pins:
            pin.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self.handle_interrupt)

    def handle_interrupt(self, pin):
        index = INPUT_PINS.index(pin.pin)
        self.responses[index] = pin.value() > THRESHHOLD

    def step(self):
        return self.responses

class OnboardControlOLD:
    def __init__(self):
        self.pins = [machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_DOWN) for pin in INPUT_PINS]

    def step(self):
        responses = [self.pins[i].value() > THRESHHOLD for i in range(4)]

        return responses

class SettingsControl:
    def __init__(self):
        self.pins = [machine.Pin(pin, machine.Pin.IN)  for pin in PINS_SETTING]

    def step(self):
        responses = [pin.value() for pin in self.pins]
        enabled_colors = [i for i in range(4) if responses[i] > THRESHHOLD]
        return enabled_colors


async def main(hero, controller, settings):
    i = 0
    while True:
        command = controller.step()
        #print(TouchCommand)
        hero.step(command)
        await asyncio.sleep_ms(5)
        i += 1
        if i > 200:
            enabled_colors = [1,1,1,1] # settings.step()
            hero.set_colors(enabled_colors)
            i = 0


if __name__ == "__main__":
    hero = SchlauchHero()
    controller = OnboardControl()
    settings = None # SettingsControl()
    loop = asyncio.get_event_loop()
    loop.create_task(main(hero, controller, settings))