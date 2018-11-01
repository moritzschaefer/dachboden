import machine
import neopixel
import random
import utime
import socket


DATA_PIN = 0 #D3
DATA_PIN_2 = 2 #D4
PIXELS = 71 #72
BUTTON_PIN = 4

class ArcadeKicker():
    start_value= (200,200,200)
    pong_color = (0,200,0)
    def __init__(self):

        self.sender = Sender(DATA_PIN, DATA_PIN_2)
        self.start_sequence()
        #self.stripes = [self.start_value for i in range(PIXELS)]
        self.time = utime.ticks_ms()
        self.pong_pos = 1
        self.stripes[self.pong_pos] = self.pong_color
        self.pong_step_time = 0.5*1000
        self.pong_inc = 1
        self.button_pressed = False
        # Not sure if Inputpin can be a class variable
        #self.button_pin = machine.Pin(BUTTON_PIN,machine.Pin.IN)
        #self.button_pin.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self.button_callback)

    def get_lights(self):
        return self.stripes

    def process_input_data(self, data):
        #TODO Do something with recieved signals
        print(data)

    def step(self):
        time_diff = utime.ticks_diff(utime.ticks_ms(), self.time)
        if self.button_pressed:
            self.strobo()
            self.button_pressed = False
        elif time_diff > self.pong_step_time:
            if(self.pong_pos+3 >= PIXELS):
                self.pong_inc = -1
                #self.strobo()
                self.select_random_special()
            elif(self.pong_pos <= 0 ):
                self.pong_inc = 1
                #self.strobo()
                self.select_random_special()
            if(self.pong_inc > 0):
                self.stripes[self.pong_pos ] = self.start_value
            else:
                self.stripes[self.pong_pos +2] = self.start_value
            self.pong_pos += self.pong_inc
            self.stripes[self.pong_pos] = self.pong_color
            self.stripes[self.pong_pos + 1] = self.pong_color
            self.stripes[self.pong_pos + 2] = self.pong_color

            self.sender.send(self.stripes)

            self.time = utime.ticks_ms

    def select_random_special(self):

        a = random.randint(0,6)
        if(a==0):
            self.random_Sparkles(n_sparks=random.randint(10,20))
        elif(a==1):
            self.strobo(random.randint(5,15))
        elif(a==2):
            self.moving_areas()
        elif(a==3):
            self.random_Sparkles(n_sparks=random.randint(10,20), color="random")
        elif(a==4):
            self.moving_areas(area_width=20, n_areas=1)
        elif(a == 5):
            self.moving_areas(n_areas=3, area_color="distinct")
        elif(a == 6):
            self.moving_areas(n_moves=2, area_color="diverse")


    def moving_areas(self,n_moves = 5, area_width=None, n_areas = None, area_color = "white"):
        if(area_width is None):
            area_width = random.randint(5,20)
        if(n_areas is None):
            n_areas = random.randint(1,4)
        if(area_color=="white"):
            color = [(200,200,200) for i in range(n_areas)]
        elif(n_areas == 3):
            color = [(200,0,0),(0,200,0),(0,0,200)]
        else:
            color= [(random.randint(0,200),random.randint(0,200),random.randint(0,200)) for i in range(n_areas)]
        board = [(0,0,0) for i in range(PIXELS)]
        viewed_pixels = PIXELS-area_width
        move_times = [random.randint(100,1500) for i in range(n_areas)]
        pos = [random.randint(0,viewed_pixels) for i in range(n_areas)]
        times = [utime.ticks_ms for i in range(n_areas)]
        counts = [0 for i in range(n_areas)]
        directions = [random.choice([-1,1]) for i in range(n_areas)]

        for i in range(n_areas):
            for j in range(area_width):
                r,g,b = board[pos[i]+j]
                r_a, g_a, b_a = color[i]
                board[pos[i] + j] =(min(200,r+r_a),min(200,g+g_a),min(200,b+b_a))
        self.sender.send(board)
        while(all([x < n_moves for x in counts])):
            changes = False
            for i in range(n_areas):
                if(utime.ticks_diff(utime.ticks_ms(),times[i]) > move_times[i]):
                    changes=True
                    if(pos[i] >= viewed_pixels):
                        directions[i] = -1
                        counts[i] += 1
                    elif(pos[i] <=0 ):
                        directions[i] = 1
                        counts[i] += 1
                    pos[i] += directions[i]
                    times[i] = utime.ticks_ms()
            if(changes):
                board = [(0,0,0) for i in range(PIXELS)}
                for i in range(n_areas):
                    for j in range(area_width):
                        r, g, b = board[pos[i] + j]
                        r_a, g_a, b_a = color[i]
                        board[pos[i] + j] = (min(200, r + r_a), min(200, g + g_a), min(200, b + b_a))
                self.sender.send(board)
            else:
                utime.sleep_ms(50)
    def random_Sparkles(self, n_sparks=15, color = "fix"):

        for i in range(n_sparks):
            spar_board = [(0, 0, 0) for i in range(PIXELS)]
            self.sender.send(spar_board)
            utime.sleep_ms(1)
            lights = random.randint(10,PIXELS-10)
            sparks = random.sample(list(range(PIXELS)),lights)
            for s in sparks:
                if(color == "fix"):
                    spar_board[s]= (200,200,200)
                elif(color == "random"):
                    spar_board[s] = (random.randint(0,200),random.randint(0,200),random.randint(0,200))

            self.sender.send(spar_board)
            utime.sleep_ms(5)


    def strobo(self, n_strobes=10):
        strobo_board_dark = [(0, 0, 0) for i in range(PIXELS)]
        strobo_board_bright = [(200, 200, 200) for i in range(PIXELS)]
        for i in range(n_strobes):
            self.sender.send(strobo_board_dark)
            utime.sleep_ms(1)
            self.sender.send(strobo_board_bright)
            utime.sleep_ms(1)
        self.sender.send(self.stripes)

    def start_sequence(self):
        self.stripes = [(0,0,0) for i in range(PIXELS)]
        for i in range(int(PIXELS/2)+2):
            self.stripes[i] = (200,0,0)
            self.stripes[-i] = (200, 0, 0)
            self.sender.send(self.stripes)
            utime.sleep_ms(20)
        for i in range(int(PIXELS/2)+2):
            self.stripes[i] = ( 0, 0, 200)
            self.stripes[-i] = (0, 0, 200)
            self.sender.send(self.stripes)
            utime.sleep_ms(20)
        for i in range(int(PIXELS/2)+2):
            self.stripes[i] = self.start_value
            self.stripes[-i] = self.start_value
            self.sender.send(self.stripes)
            utime.sleep_ms(10)

    def time_out(self, player):
        pass

    def button_callback(self, pin):
        self.button_pressed = True


class Sender():
    def __init__(self, pin, pin2 = None):

        self.neop = neopixel.NeoPixel(machine.Pin(pin), PIXELS)
        if pin2 is not None:
            self.neop2 = neopixel.NeoPixel(machine.Pin(pin2), PIXELS)

    def send(self, pixel_values):
        for i in range(PIXELS):
            self.neop[i] = pixel_values[i]
            self.neop2[i] = pixel_values[i]
        self.neop.write()
        self.neop2.write()

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



