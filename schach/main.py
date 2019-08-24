import machine
import neopixel
from math import sin
import utime
import uos
import socket
import array
import Ambiente
import stroboscope
import startup
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
        startup.startoup(self.sender, self.player_pixel, self.player_colors)
        print("One Startup finished")

        self.Counter = 0
        self.ambiente = Ambiente.Ambiente(self.sender)
        self.mode = "ambiente"
        self.time_progress = 0

        self.player_time = 60*1000*5
        self.game_time = (self.player_time,self.player_time)


    def get_lights(self):
        return self.board

    def process_input_data(self, data):
        #TODO Do something with recieved signals
        print(data)

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
        self.game_time = (self.player_time, self.player_time)
        self.mode = "live"

    def set_player_time(self, time):
        self.player_time = time * 1000 * 60

    def set_color(self, player, color):
        self.player_colors[player] = color

    def step(self):
        time_diff = utime.ticks_diff(utime.ticks_ms(),self.time)
        if self.mode == "ambiente":
            self.ambiente.ambiente_step()
        elif self.mode == "live":
            if time_diff > self.game_time[self.player]:
                self.time_out(player = self.player)
            else:
                pass
            #elif  self.game_time[self.player] - time_diff > self.time_progress * self.game_time[self.player]:
            #TODO Let the led loose progress

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

class Receiver():
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.sock.close()

    def __init__(self,buffer_size=64):
        self.buffer_size = buffer_size

        #Bind the socket to the port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        server_address = ('0.0.0.0', 9000)
        self.sock.bind(server_address)
        self.sock.settimeout(0.1)

    def receive(self):
        try:
            data, _ = self.sock.recvfrom(self.buffer_size)

        except OSError:  # timeout!!
            return None
        except Exception as e:
            print(e)
            return None
        else:
            return data

def ambiente_light(self):
    pass

def main():
    chess = Chess()
    with Receiver() as recv:
        while True:
            """
            data = recv.receive()
            if data is not None:
                chess.process_input_data(data)
            """
            chess.step()



class ApiHandler:
    def __init__(self, chess):
        self.chess = chess

    def index(self):
        return "" # TODO add HTML

    def get(self, api_request):
        print(api_request)
        # TODO Not sure if bullshit or handled right, see https://github.com/fadushin/esp8266/tree/master/micropython/uhttpd  Api Handlers... Inputs
        operation =  api_request['query_params'].get('operation', 'index')
        if 'white_player_done' == operation:
            self.chess.set_turn("black")
        elif 'black_player_done' == operation:
            self.chess.set_turn("white")
        elif 'restart' == operation:
            self.chess.restart()
        elif 'set_time'  == operation:
            value = int(api_request['query_params']['value'])
            self.chess.set_player_time(value)
        elif 'set_white_color':
            html_color = api_request['query_params']['value']
            value = tuple(int(html_color[i:i+2], 16) for i in (0, 2, 4))
            self.chess.set_color(player=0, color=value)
        elif 'set_black_color':
            html_color = api_request['query_params']['value']
            value = tuple(int(html_color[i:i+2], 16) for i in (0, 2, 4))
            self.chess.set_color(player=1, color=value)
        elif operation == 'index':
            return self.index()


if __name__ == "__main__":
    main()
    api_handler = http_api_handler.Handler([([''], ApiHandler(modules))])
    loop = asyncio.get_event_loop()
    loop.create_task(main(modules))
    server = uhttpd.Server([('/api', api_handler)])
    server.run()



#TODO
#Move async to esp
#async http soket.
#IP websocket 192.168.178.4
# Website:

#  Two time fields as buttons
#  Send two signals
#  TODO learn how to display live changing time



# Modules:
"""
DMX Strobo Access (not interupting the time)

Intern Network:
Time is running down /Different color 

Settings: (Color for each player, Time per match, increment, delay )  
Each player is slowling losing color for each turn. You see the delay/increment first cycle and then the overall time starts per turn and goes in the right speed. 5 sec left, very fast, 5 min left very slowe
 

"""


#Sonstiges
#Milchglas