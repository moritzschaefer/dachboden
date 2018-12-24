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
    start_value=[(150,0,0),(0,150,0)]

    def __init__(self):
        pixel_w = int(PIXELS/2)
        self.pixel_per_player = (pixel_w, PIXELS-pixel_w)
        self.player = 0
        self.turn_time = 15*1000
        self.time = utime.ticks_ms()
        self.player_pixel = []
        self.player_pixel.append([self.start_value[0] for i in range(self.pixel_per_player[0])])
        self.player_pixel.append([self.start_value[1] for i in range(self.pixel_per_player[1])])
        print(len(self.player_pixel))
        print(len(self.player_pixel[0]), len(self.player_pixel[1]))
        self.board = self.player_pixel[0] + self.player_pixel[1]
        self.light=0
        self.sender = Sender()

        self.sender.send(self.board)
        #utime.sleep_ms(15000)

        #stroboscope.stroboscope(self.sender, self.board)
        startup.startup(self.sender, self.player_pixel, self.start_value)
        print("One Startup finished")

        self.Counter = 0
        self.ambiente = Ambiente.Ambiente(self.sender)
        while True:
            self.ambiente.ambiente_step()

    def get_lights(self):
        return self.board

    def process_input_data(self, data):
        #TODO Do something with recieved signals
        print(data)

    def step(self):
        time_diff = utime.ticks_diff(utime.ticks_ms(),self.time)

        if(self.Counter >= MAX_ROTATIONS):
            self.ambiente.ambiente_step()
            return
        if time_diff > self.turn_time:
            self.player_restart()
        elif time_diff > self.light * (self.turn_time/ (self.pixel_per_player[self.player])):

            #print("Length of Pixel", len(self.player_pixel[0]), len(self.player_pixel[1]))
            #self.player_pixel[self.player][self.light] = tuple(map(lambda a: int(a*0.1), self.start_value[self.player]))
            self.board[self.light + self.player * self.pixel_per_player[0]] = tuple(
                map(lambda a: int(a * 0.1), self.start_value[self.player]))

            self.light = min(self.light+1, self.pixel_per_player[self.player]-1)
            #print(self.light, "licht")
            self.board[self.light + self.player * self.pixel_per_player[0]] = ( self.start_value[self.player][0],
                                                                                self.start_value[self.player][1], 150)

            board_copy = self.board.copy()

            self.sender.send(self.board)


    def player_restart(self):
        self.player_pixel[self.player] = [ self.start_value[self.player] for i in self.player_pixel[self.player]]
        self.board = self.player_pixel[0] + self.player_pixel[1]
        self.light = 0
        self.time = utime.ticks_ms()
        self.player = (self.player + 1) % 2
        self.sender.send(self.board)

        self.Counter += 1


    def time_out(self, player):
        pass


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



if __name__ == "__main__":
    main()
