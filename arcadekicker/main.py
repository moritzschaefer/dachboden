import machine
import neopixel

import utime
import socket


DATA_PIN = 2
PIXELS = 100


class ArcadeKicker():
    start_value= (200,200,200)
    pong_color = (0,200,0)
    def __init__(self):

        self.sender = Sender()
        self.start_sequence()
        #self.stripes = [self.start_value for i in range(PIXELS)]
        self.time = utime.ticks_ms()
        self.pong_pos = 0
        self.stripes[self.pong_pos] = self.pong_color
        self.pong_step_time = 0.5*1000
        self.pong_inc = 1

    def get_lights(self):
        return self.stripes

    def process_input_data(self, data):
        #TODO Do something with recieved signals
        print(data)

    def step(self):
        time_diff = utime.ticks_diff(utime.ticks_ms(), self.time)
        if time_diff > self.pong_step_time:
            if(self.pong_pos+1 >= PIXELS):
                self.pong_inc = -1
            elif(self.pong_pos <=0 ):
                self.pong_inc = 1

            self.stripes[self.pong_pos] = self.start_value
            self.pong_pos += self.pong_inc
            self.stripes[self.pong_pos] = self.pong_color

            self.sender.send(self.stripes)

            self.time = utime.ticks_ms

    def start_sequence(self):
        self.stripes = [(0,0,0) for i in range(PIXELS)]
        for i in range(PIXELS):
            self.stripes[i] = (200,0,0)
            self.sender.send(self.stripes)
            utime.sleep_ms(20)
        for i in range(PIXELS):
            self.stripes[i] = ( 0, 0, 200)
            self.sender.send(self.stripes)
            utime.sleep_ms(20)
        for i in range(PIXELS):
            self.stripes[i] = self.start_value
            self.sender.send(self.stripes)
            utime.sleep_ms(10)

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


def main():
    arckick = ArcadeKicker()
    with Receiver() as recv:
        while True:
            data = recv.receive()
            if data is not None:
                arckick.process_input_data(data)

            arckick.step()



if __name__ == "__main__":
    main()



