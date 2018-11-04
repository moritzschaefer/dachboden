import machine
import neopixel
import utime
import uos
import socket
import array

DATA_PIN = 4
PIXELS = 54


class DachbodenSchild():
    start_value=(150,0,0)
    step_time = 50
    color_time = 1
    width = 27
    def __init__(self):

        self.color = (150,0,0)
        self.stripe = [self.color for i in range(PIXELS)]
        self.sender = Sender()
        self.sender.send(self.stripe)
        self.time = utime.ticks_ms()
        #self.width = 10
        self.position = 0
        self.ctime = utime.ticks_ms()
        self.color_mode = 0 # 0: Blue rising, 1: Red sinking, 2: Red rising, 3: Blue sinking
    def move_right(self):
        self.position = (self.position +1) % PIXELS
        for i in range(PIXELS):
            if(self.position == i or  i == (self.position + self.width) % PIXELS ):
                self.stripe[i] = (int(self.color[0] * 0.5),int(self.color[1] * 0.5),int(self.color[2] * 0.5))
            elif((self.position  % PIXELS) <= i <= self.position+ self.width):
                self.stripe[i] = self.color
            elif(i <=(self.position+ self.width) % PIXELS and (self.position+ self.width) % PIXELS  <= self.position):
                self.stripe[i] = self.color
            else:
                self.stripe[i] = (0, 0, 0)

    def change_color(self):
        if((self.color_mode == 0 and self.color[2] >= 150) or (self.color_mode ==1 and self.color[0] <=0 ) or (self.color_mode ==2 and self.color[0] >=150)):
            self.color_mode += 1
        elif(self.color_mode == 3 and self.color[2] <=0):
            self.color_mode = 0

        if(self.color_mode ==0):
            self.color = (self.color[0],self.color[1],self.color[2]+1)

        elif (self.color_mode == 1):
            self.color = (self.color[0]-1, self.color[1], self.color[2])

        elif (self.color_mode == 2):
            self.color = (self.color[0] +1, self.color[1], self.color[2])

        elif (self.color_mode == 3):
            self.color = (self.color[0], self.color[1], self.color[2]-1)

    def step(self):
        if(abs(utime.ticks_diff(self.time, utime.ticks_ms())) > self.step_time):
            print("Move to right")
            self.move_right()
            self.time = utime.ticks_ms()


        if (abs(utime.ticks_diff(self.ctime, utime.ticks_ms())) > self.color_time):
            print("Change color ", self.color)
            self.change_color()
            self.color_time = utime.ticks_ms()
        self.sender.send(self.stripe)

    def get_lights(self):
        return self.stripe


    def process_input_data(self, data):
        #TODO Do something with recieved signals
        print(data)

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
    schild = DachbodenSchild()
    while True:
        schild.step()
    """
    with Receiver() as recv:
        while True:
            data = recv.receive()
            if data is not None:
                schild.process_input_data(data)

            schild.step()
    """


if __name__ == "__main__":
    main()




