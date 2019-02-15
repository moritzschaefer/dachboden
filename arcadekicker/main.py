import machine
import neopixel
import utime
import socket
import lightshow
import random
import gc
import uos
import sys
#TODO random

DATA_PIN = 0 #D3
DATA_PIN_2 = 2 #D4
PIXELS = 71 #72
BUTTON_PIN = 4

class ArcadeKicker():
    start_value= (200,200,200)
    pong_color = (0,200,0)

    def __init__(self):
        self.sender = Sender(DATA_PIN, DATA_PIN_2)
        if(random.randint(0,1000) % 2):
            self.normal_mode = True
            self.stripes = [(200, 200, 200) for i in range(PIXELS)]
            self.sender.send(self.stripes)
        else:
            self.normal_mode = False
            self.start_sequence()
        #self.stripes = [self.start_value for i in range(PIXELS)]
        self.time = utime.ticks_ms()
        self.pong_pos = 1
        self.stripes[self.pong_pos] = self.pong_color
        #self.pong_step_time = 0.5*1000
        self.pong_step_time = 0.5 * 10
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
        if self.normal_mode:
            return
        time_diff = utime.ticks_diff(utime.ticks_ms(), self.time)
        try:
            #if self.button_pressed:
            #Here the codes crashes and game become normal, its not a bug its a feature, just touch pin 4
            #    self.button_pressed = False
            if time_diff > self.pong_step_time:
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

        except Exception as e:
            #exc_type, exc_obj, exc_tb = sys.exc_info()
            #print(exc_type, exc_tb.tb_lineno)
            print("Intern Error in step function", e)

    def select_random_special(self):
        if(random.randint(0,100) < 66):
            return
        a = random.randint(0,9)
        #a = 2
        if a in (1,2):
            return
            #a= 2
        if(a==0):
            lightshow.random_Sparkles(self.sender,self.stripes, n_sparks=random.randint(50,100), strobo_mode= False, sleep_time= 5, max_lights = 40)
        elif(a==1):
            lightshow.strobo(self.sender, self.stripes, random.randint(20,40))
        elif(a==2):
            lightshow.moving_areas(self.sender, self.stripes)
        elif(a==3):
            lightshow.random_Sparkles(self.sender, self.stripes, n_sparks=random.randint(40,100), color="random")
        elif(a==4):
            lightshow.ongoing_lights(self.sender, self.stripes )
        elif(a == 5):
            lightshow.moving_areas(self.sender, self.stripes, n_moves= random.randint(5,20),n_areas=3, area_color="distinct")
        elif(a == 6):
            lightshow.moving_areas(self.sender,self.stripes, n_moves= random.randint(5,20), area_color="diverse")
        elif(a == 7):
            lightshow.random_Sparkles(self.sender, self.stripes, n_sparks=random.randint(50,250), color = "random", ring=True, strobo_mode = False, sleep_time = 10)
        elif(a == 8):
            lightshow.moving_areas(self.sender, self.stripes, area_width=40, n_areas=3, n_moves = 5)

        self.stripes = [self.start_value for i in range(PIXELS)]

        gc.collect()

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
    arcadekicker = ArcadeKicker()
    while True:
        try:
            arcadekicker.step()
        except Exception as e:
            print("Error in step function", e)

    """
    with Receiver() as recv:
        while True:
            data = recv.receive()
            if data is not None:
                arckick.process_input_data(data)
            arckick.step()
    """


if __name__ == "__main__":
    main()



