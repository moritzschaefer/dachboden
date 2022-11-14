import http_api_handler
import uhttpd
import uasyncio as asyncio
import machine
import neopixel
#from math import sin
import utime
#import os
#import uos
import socket
#import array
import ambiente
#import stroboscope
#import startup
#import random
# Channels: 151

# 0 mode
# 1,2,3 RGB Pixel 0
# 4,5,6 RGB Pixel 1
# ...

DATA_PIN = 4

#TOUCHPINS 0,2,4,12,13,14,15,27,32,33
PINWHITE = 14
PINBLACK = 13
PINMODE = 32
SENSITIVITY = 600
THRESHHOLD = 150
PIXELS = 102
MAX_ROTATIONS = 20
INTENSITY = 0.8

class Chess:
    player_colors=[(75,0,0),(0,75,0)]

    def __init__(self):
        pixel_w = int(PIXELS/2)
        self.pixel_per_player = (pixel_w, PIXELS-pixel_w)
        self.player = 0
        self.turn_time = 15*1000
        self.time = utime.ticks_ms()
        self.player_pixel = []
        self.player_pixel.append([self.player_colors[0] for i in range(self.pixel_per_player[0])])
        self.player_pixel.append([self.player_colors[1] for i in range(self.pixel_per_player[1])])
        print(len(self.player_pixel))
        print(len(self.player_pixel[0]), len(self.player_pixel[1]))
        self.board = self.player_pixel[0] + self.player_pixel[1]
        self.light=0
        self.sender = Sender()

        self.sender.send(self.board)
        #utime.sleep_ms(15000)

        #stroboscope.stroboscope(self.sender, self.board)
        #startup.startup(self.sender, self.player_pixel, self.player_colors)
        print("One Startup finished")

        self.Counter = 0
        if True: #random.randint(0,2)>=1:
            self.ambiente = ambiente.Ambiente(self.sender, n_pixels=PIXELS)

        #self.mode = "live"
        self.mode = "pause"
        self.time_progress = 0

        self.player_time = 60*1000*5
        self.game_time = [self.player_time, self.player_time]
        self.web_time = [self.player_time, self.player_time]

        self.game_modus = 0

    def get_lights(self):
        return self.board


    def set_turn(self, player, time=None):
        if player == "white":
            self.player = 0
        elif player == "black":
            self.player = 1
        else:
            print("Could not get the player turn")
        self.mode = "live"
        self.game_time[not self.player] -= utime.ticks_diff(utime.ticks_ms(), self.time)
        if time is not None:
            self.web_time[self.player] = time
        self.board = [self.player_colors[self.player] for x in self.board]
        self.sender.send(self.board)
        self.time = utime.ticks_ms()
        self.time_progress = 0
        print("Time difference between web and controller",  self.web_time, self.game_time)


    def restart(self):
        self.game_time = [self.player_time, self.player_time]
        self.web_time = [self.player_time, self.player_time]
        self.mode = "pause"

    def set_player_time(self, time):
        self.player_time = time * 1000 * 60

    def set_color(self, player, color):
        self.player_colors[player] = tuple([int(x * INTENSITY) for x in color])
        self.board = [self.player_colors[player] for x in self.board]
        self.sender.send(self.board)
        self.ambiente.set_color(player, self.player_colors[player])
        self.ambiente.moving_slides_init(4)

    def pause(self):
        self.game_time[self.player] -= utime.ticks_diff(utime.ticks_ms(), self.time)
        self.mode = "pause"

    def pause_or_play(self):
        if self.mode == "pause":
            self.start()
        else:
            self.pause()

    def start(self):
        self.time = utime.ticks_ms()
        self.board = [self.player_colors[self.player] for x in self.board]
        self.sender.send(self.board)
        self.time_progress = 0
        self.mode = "live"


    def step(self):
        time_diff = abs(utime.ticks_diff(utime.ticks_ms(), self.time))
        if self.mode == "ambiente":
            self.ambiente.step()
        elif self.mode == "live":
            if time_diff > self.web_time[self.player]: #Time has been running down
                print("Time is out")
                self.time_out(player = self.player)
            elif (self.web_time[self.player] * (self.time_progress / PIXELS)) < time_diff: #Next pixel lights out
                    print("Pixel is fading out", time_diff, self.time_progress)
                    #self.time_progress += 1
                    self.time_progress = (time_diff  * PIXELS ) // self.web_time[self.player] + 1
                    for i in range(self.time_progress):
                        self.board[i] = (10, 10, 10)
                    self.sender.send(self.board)
            else:
                pass

        elif self.mode == "pause":
            self.ambiente.step()
        else:
            self.arcade_mode_step(time_diff)


    def arcade_mode_step(self, time_diff):
        if (self.Counter >= MAX_ROTATIONS):
            self.ambiente.step()
            return
        if time_diff > self.turn_time:
            self.player_restart()
        elif time_diff > self.light * (self.turn_time / (self.pixel_per_player[self.player])):

            # print("Length of Pixel", len(self.player_pixel[0]), len(self.player_pixel[1]))
            # self.player_pixel[self.player][self.light] = tuple(map(lambda a: int(a*0.1), self.player_colors[self.player]))
            self.board[self.light + self.player * self.pixel_per_player[0]] = tuple(
                map(lambda a: int(a * 0.1), self.player_colors[self.player]))

            self.light = min(self.light + 1, self.pixel_per_player[self.player] - 1)
            # print(self.light, "licht")
            self.board[self.light + self.player * self.pixel_per_player[0]] = (self.player_colors[self.player][0],
                                                                               self.player_colors[self.player][1], 150)

            #board_copy = self.board.copy()

            self.sender.send(self.board)

    def player_restart(self):
        self.player_pixel[self.player] = [ self.player_colors[self.player] for i in self.player_pixel[self.player]]
        self.board = self.player_pixel[0] + self.player_pixel[1]
        self.light = 0
        self.time = utime.ticks_ms()
        self.player = (self.player + 1) % 2
        self.sender.send(self.board)
        self.Counter += 1


    def loop_modus(self):
        pass
        #3min 3s Increment

        #5min 5s Increment

        #10min 5s Increment

        #1min 1s Increment

    def time_out(self, player):
        for i in range(20):
            self.board = [tuple([i % 2 * 10] * 3) for _ in self.board]
            self.sender.send(self.board)
            utime.sleep_ms(100)
        self.mode = "ambiente"

class Sender():
    def __init__(self):
        self.neop = neopixel.NeoPixel(machine.Pin(DATA_PIN), PIXELS)

    def send(self, pixel_values):
        for i in range(PIXELS):
            self.neop[i] = pixel_values[i]
        self.neop.write()

class OnboardControl():
    def __init__(self):

        self.black = machine.TouchPad(machine.Pin(PINBLACK))
        self.white = machine.TouchPad(machine.Pin(PINWHITE))
        self.mode = machine.TouchPad(machine.Pin(PINMODE))
        print(PINMODE,PINWHITE,PINBLACK)
        #self.black.config(SENSITIVITY)
        #self.white.config(SENSITIVITY)
        #self.mode.config(SENSITIVITY)

        self.b = 0
        self.w = 0
        self.m = 0

        self.last_pause_time = utime.ticks_ms()
    def step(self, chess):

        b = self.black.read() < THRESHHOLD
        w = self.white.read() < THRESHHOLD
        m = self.mode.read() < THRESHHOLD
        #print("Reading B:", b, " W:", w, " M:",m)
        if b and self.b and w and self.w and m and self.m:
            #print("Restart")
            chess.restart()
            answer = "Restart"

        elif b and self.b and w and self.w:
            answer = "both"
        elif b and self.b:
            answer = "black_played"
            chess.set_turn("white")
        elif w and self.w:
            answer = "white played"
            chess.set_turn("black")
        elif m and self.m:
            if utime.ticks_diff(utime.ticks_ms(), self.last_pause_time) > 2000:
                #print("pause")
                answer = "pause/continue"
                chess.pause_or_play()
                self.last_pause_time = utime.ticks_ms()
            else:
                #print(utime.ticks_diff(self.last_pause_time, utime.ticks_ms()))
                answer = "tried to pause"
            #answer = "ModeButton"
        else:
            answer = "nothing"+str(self.black.read())+str(self.white.read())+str(self.mode.read())
        self.b = b
        self.w = w
        self.m = m

        return answer

async def main(chess, controller):
    #chess = Chess()
    while True:
        TouchCommand = controller.step(chess)
        #print(TouchCommand)
        chess.step()
        await asyncio.sleep_ms(10)


class ApiHandler:
    def __init__(self, chess):
        self.chess = chess
        file = open("index.html")
        self.INDEX = str(file.read())
        file.close()
    def index(self):
        return self.INDEX
    def get(self, api_request):
        print("Der Apirequest ist angekommen :")
        print(api_request)
        operation =  api_request['query_params'].get('operation', 'index')
        if 'player_black' == operation:
            value = int(api_request['query_params']['value'])
            print("Blacks turn now")
            self.chess.set_turn("black", time=value)
        elif 'player_white' == operation:
            value = int(api_request['query_params']['value'])
            print("Whites turn now")
            self.chess.set_turn("white", time=value)
        elif 'restart' == operation:
            print("Restart Game")
            self.chess.restart()
        elif 'start' == operation:
            print("Starting a Game")
            self.chess.start()
        elif 'pause' == operation:
            print("Pausing the Game")
            self.chess.pause()
        elif 'set_time'  == operation:
            value = int(api_request['query_params']['value'])
            print("Set time to ", value)
            self.chess.set_player_time(value)
        elif 'set_color_white' == operation:
            html_color = api_request['query_params']['value']
            value = tuple(int(html_color[i:i+2], 16) for i in (0, 2, 4))
            print("Set white color to ", value)
            self.chess.set_color(player=0, color=value)
        elif 'set_color_black' == operation:
            html_color = api_request['query_params']['value']
            value = tuple(int(html_color[i:i+2], 16) for i in (0, 2, 4))
            print("Set black color to ", value)
            self.chess.set_color(player=1, color=value)
        elif operation == 'index':
            print("Der Nutzer wollte die Website sehen")
            return self.INDEX
        elif operation == 'hello':
            print("Hello world")
            return('''
            <!DOCTYPE html>
             <html> 
              <header> 
              <title> EasterEgg: </title> 
              </header> 
              <body> Hello  world </body>
              </html>''')


if __name__ == "__main__":
    chess = Chess()
    controller = OnboardControl()
    api_handler = http_api_handler.Handler([([''], ApiHandler(chess))])
    loop = asyncio.get_event_loop()
    loop.create_task(main(chess, controller))
    server = uhttpd.Server([('/api', api_handler)])
    server.run()

