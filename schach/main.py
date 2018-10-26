import machine
import neopixel
from math import sin
import utime
import uos
import socket
import array

# Channels: 151

# 0 mode
# 1,2,3 RGB Pixel 0
# 4,5,6 RGB Pixel 1
# ...

DATA_PIN = 2
PIXELS = 97


class Chess():
    start_value=[(200,0,0),(0,200,0)]

    def __init__(self):
        self.pixel_per_player = int(PIXELS/2)
        self.player = 0
        self.turn_time = 15*1000
        self.time = utime.ticks_ms()
        self.player_pixel = []
        self.player_pixel.append([self.start_value[0] for i in range(int(PIXELS/2))])
        self.player_pixel.append([self.start_value[1] for i in range(int(PIXELS / 2)+1)])
        self.board = self.player_pixel[0] + self.player_pixel[1]
        #self.board = [(0,0,0) for i in range(PIXELS)]
        self.light=0
    def get_lights(self):
        return self.board

    def process_input_data(self, data):
        #TODO Do something with recieved signals
        print(data)

    def step(self):
        time_diff = utime.ticks_diff(utime.ticks_ms(),self.time)
        if time_diff > self.turn_time:
            self.player_restart()
        elif time_diff > self.light * (self.turn_time/ (self.pixel_per_player+self.player)):
            self.player_pixel[self.light] = (self.start_value[self.player]*0.3)
            self.light += 1
            self.board = self.player_pixel[0] + self.player_pixel[1]

    def player_restart(self):
        self.player_pixel[self.player] = [ self.start_value[self.player] for i in self.player_pixel[self.player]]
        self.board = self.player_pixel[0] + self.player_pixel[1]
        self.light = 0
        self.time = utime.ticks_ms()
        self.player = (self.player + 1) % 2

    def time_out(self, player):
        pass


class Sender():
    def __init__(self):
        self.neop = neopixel.NeoPixel(machine.Pin(DATA_PIN), PIXELS)

    def send(self, pixel_values):
        for i in range(PIXELS):
            self.neop[i] = pixel_values(i)
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


def main():
    chess = Chess()
    sender = Sender()
    with Receiver() as recv:
        while True:
            data = recv.receive()
            if data is not None:
                chess.process_input_data(data)

            chess.step()
            pixel_values = chess.get_lights()
            sender.send(pixel_values)



if __name__ == "__main__":
    main()



