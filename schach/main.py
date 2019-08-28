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
#import ambiente
#import stroboscope
#import startup

# Channels: 151

# 0 mode
# 1,2,3 RGB Pixel 0
# 4,5,6 RGB Pixel 1
# ...

DATA_PIN = 2
PIXELS = 97
MAX_ROTATIONS = 20


class Chess:
    player_colors=[(150,0,0),(0,150,0)]

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
        #self.ambiente = ambiente.Ambiente(self.sender)
        #self.mode = "ambiente"
        self.mode = "live"
        self.time_progress = 0

        self.player_time = 60*1000*5
        self.game_time = [self.player_time,self.player_time]


    def get_lights(self):
        return self.board


    def set_turn(self, player):
        if player == "white":
            player = 0
        elif player == "black":
            player = 1
        else:
            print("Could not get the player turn")

        self.game_time[self.player] -= utime.ticks_diff(utime.ticks_ms(), self.time)
        self.player = player
        self.board = [self.player_colors[self.player] for x in self.board]
        self.sender.send(self.board)
        self.time = utime.ticks_ms()
        self.time_progress = 0



    def restart(self):
        self.game_time = [self.player_time, self.player_time]
        self.mode = "live"

    def set_player_time(self, time):
        self.player_time = time * 1000 * 60

    def set_color(self, player, color):
        self.player_colors[player] = color

    def step(self):
        time_diff = abs(utime.ticks_diff(utime.ticks_ms(), self.time))
        if self.mode == "ambiente":
            self.ambiente.ambiente_step()
        elif self.mode == "live":
            if time_diff > self.game_time[self.player]:
                self.time_out(player = self.player)
            elif  (self.game_time[self.player] * self.time_progress / PIXELS)  >  time_diff :
                    self.time_progress += 1
                    for i in range(self.time_progress):
                        self.board[i] = (10, 10, 10)
                    self.sender.send(self.board)
            else:
                pass

        else:
            self.arcade_mode_step(time_diff)


    def arcade_mode_step(self, time_diff):
        if (self.Counter >= MAX_ROTATIONS):
            self.ambiente.ambiente_step()
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

            board_copy = self.board.copy()

            self.sender.send(self.board)

    def player_restart(self):
        self.player_pixel[self.player] = [ self.player_colors[self.player] for i in self.player_pixel[self.player]]
        self.board = self.player_pixel[0] + self.player_pixel[1]
        self.light = 0
        self.time = utime.ticks_ms()
        self.player = (self.player + 1) % 2
        self.sender.send(self.board)

        self.Counter += 1


    def time_out(self, player):
        for i in range(20):
            self.board = [tuple([i % 2 * 200] * 3) for _ in self.board]


class Sender():
    def __init__(self):
        self.neop = neopixel.NeoPixel(machine.Pin(DATA_PIN), PIXELS)

    def send(self, pixel_values):
        for i in range(PIXELS):
            self.neop[i] = pixel_values[i]
        self.neop.write()



async def main(chess):
    #chess = Chess()
    while True:
        chess.step()

        await asyncio.sleep_ms(10)



class ApiHandler:
    def __init__(self, chess):
        self.chess = chess
        self.file = open("index.html")
    def index(self):
        return self.file.read()

    def get(self, api_request):
        print(api_request)
        operation =  api_request['query_params'].get('operation', 'index')
        if 'player_white' == operation:
            print("Blacks turn now")
            self.chess.set_turn("black")

        elif 'player_black' == operation:
            print("Whites turn now")
            self.chess.set_turn("white")
        elif 'restart' == operation:
            print("Restart Game")
            self.chess.restart()
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
            return self.index()


if __name__ == "__main__":
    chess = Chess()
    api_handler = http_api_handler.Handler([([''], ApiHandler(chess))])
    loop = asyncio.get_event_loop()
    loop.create_task(main(chess))
    server = uhttpd.Server([('/api', api_handler)])
    server.run()



