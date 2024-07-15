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
LIFE_PINS = [25, 26]
SCORE_PINS = [32, 33]
THRESHHOLD = 150
PIXELS = 5*60
VERBOSE = False

def smart_print(string, *args):
    if VERBOSE:
        print(string, *args)
        
class SchlauchHero:
    colors=[(200,0,0), (0,200,0), (0,0,200), (200,0,200), (200,200,200), (0,0,0)]
    level_speed = [100, 75, 50, 25, 10]
    ball_speed = 5
    width = 10
    light = 0
    def __init__(self):
        self.int_board = [4 for i in range(PIXELS)]
        self.board = [self.colors[i] for i in self.int_board]
        self.sender = Sender()
        self.score_monitor = tm1637.TM1637(clk=machine.Pin(SCORE_PINS[0]), dio=machine.Pin(SCORE_PINS[1]))
        self.life_monitor = tm1637.TM1637(clk=machine.Pin(LIFE_PINS[0]), dio=machine.Pin(LIFE_PINS[1]))
        self.sender.send(self.board)
        self.restart()
        self.current_colors = [0, 1, 2, 3]
        self.ball_width = 8
        self.ball_board = [-1 for _ in range(PIXELS)] # Stores color and pos of ball
        self.change = 0
        
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
        self.life = 10
        self.score = 0
        self.cur_generation_width = 0
        self.cur_generation_color = 4

        self.time = utime.ticks_ms()
        self.button_time = utime.ticks_ms()
        self.ball_time = utime.ticks_ms()
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
                smart_print("You Scored a Point", self.score)
                # Correct
                self.int_board[self.light] = 4 # Some reward
                self.score += 1
                self.update_score()
                self.point_sequence(pressed[0])
            else:
                # Wrong
                smart_print("You lost a life", self.life)
                self.life -= 1
                self.update_life()
                self.point_sequence(-1)
                if self.life <= 0:
                    self.loose_sequence()
                    self.restart()


    def loose_sequence(self):
        # Let all lights strobe
        smart_print("Game Lost :( ")
        for i in range(PIXELS):
            self.ball_board[i] = -1
            self.int_board[i] = -1
        for _ in range(5):
            for i in range(PIXELS):
                self.board[i] = self.colors[-2]
            self.sender.send(self.board)
            utime.sleep_ms(25)
            for i in range(PIXELS):
                self.board[i] = self.colors[-1]
            self.sender.send(self.board)
            utime.sleep_ms(25)

    def point_sequence(self, color):
        # Send the color as a ball in opposite direction
        for i in range(self.ball_width):
            self.ball_board[i] = color

    def merge_ball_and_board(self):
        for i in range(PIXELS):
            if self.ball_board[i] >= 0:
                self.board[i] = self.colors[self.ball_board[i]]
            else:
                self.board[i] = self.colors[self.int_board[i]]

    def move_ball(self):
        for i in range(1, PIXELS):
            self.ball_board[PIXELS - i] = self.ball_board[PIXELS - i - 1]
        self.ball_board[0] = -1
    def move_color(self):
        # Move the light, randomly spawn a new color
        for i in range(PIXELS-1):
            self.int_board[i] = self.int_board[i+1]
            #self.board[i] = self.colors[self.int_board[i]]

        if self.cur_generation_width <= 0:
            if randint(0,100) > 25:
                if len(self.current_colors) == 0:
                    self.cur_generation_color = randint(0,4)
                else:
                    self.cur_generation_color = self.current_colors[randint(0,len(self.current_colors))]
                self.cur_generation_width = self.width
            else:
                # Generate some dark pixels
                self.cur_generation_color = -1
                self.cur_generation_width = self.width // 2
            smart_print("Added new Color: ", self.cur_generation_color)
        self.int_board[PIXELS-1] = self.cur_generation_color
        #self.board[PIXELS-1] = self.colors[self.cur_generation_color]
        self.cur_generation_width -= 1

    def send_color(self, command):
        pressed = [i for i in range(4) if command[i]]

        if len(pressed) == 1:
            for i in range(1, PIXELS):
                self.int_board[i] = self.int_board[i - 1]
                self.board[i] = self.colors[self.int_board[i]]

            self.int_board[0] = pressed[0]
            self.board[0] = self.colors[pressed[0]]

    def step(self, command):

        if self.mode == "sending":
            self.send_color(command)
            self.change = 1
        else:
            if utime.ticks_ms() - self.button_time > 50:
                self.check_correct(command)

            # Check if time is ready to move the light
            if utime.ticks_ms() - self.time > self.level_speed[min(self.score//10,len(self.level_speed))]:
                self.time = utime.ticks_ms()
                self.move_color()
                self.change = 1

            if utime.ticks_ms() - self.ball_time > self.ball_speed:
                self.ball_time = utime.ticks_ms()
                self.move_ball()
                self.change = 1

        if self.change:
            self.merge_ball_and_board()
            self.sender.send(self.board)
            self.change=0


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
        self.responses = [0] * len(INPUT_PINS)
        self.changed = 0
        for pin in self.pins:
            pin.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self.handle_interrupt)
        

    def handle_interrupt(self, pin):
        index = INPUT_PINS.index(int(str(pin)[4:-1]))
        self.responses[index] = pin.value()
        self.changed = 1

    def step(self):
        if self.changed:
            self.changed = 0
            return self.responses, 1
        else:
            return self.responses, 0

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
        command, change = controller.step()
        if change:
            smart_print("We observed this command: ", command)
            hero.step(command)
        else:
            hero.step([0,0,0,0])
        await asyncio.sleep_ms(5)
        i += 1
        if i > 200:
            enabled_colors = [0,1,2,3] # settings.step()
            hero.set_colors(enabled_colors)
            i = 0

smart_print(__name__)

if __name__ == "__main__":
    print("Starting GAME")
    hero = SchlauchHero()
    controller = OnboardControl()
    settings = None # SettingsControl()
    #loop = asyncio.get_event_loop()
    #loop.create_task(main(hero, controller, settings))
    #loop.run_forever()
    asyncio.run(main(hero, controller, settings))
