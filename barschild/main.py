import machine, neopixel, time
import utime #for strobo
import random
import uos
import http_api_handler
import uhttpd
import socket
import neopixel
import uasyncio as asyncio

PIN = 14 # was 2 on ESP-8622
NUM_PIXEL = 75
INTENSITY = 40

RED = (16, 0, 0)
GREEN = (1, 8, 0)
YELLOW = (15, 15, 0)
WHITE = (100, 80, 40)
BLACK = (0, 0, 0)
STROBO = (220,220,220)

np = neopixel.NeoPixel(machine.Pin(PIN), NUM_PIXEL)

drinks = [''] * 73 # correct???
drinks[3] = 'special'
drinks[4] = 'spezi'
drinks[5] = 'mate'
drinks[7] = 'shot'
drinks[49] = 'beer'
drinks[51] = 'nonalcoholicBeer'
drinks[52] = 'radler'
drinks[53] = 'fizz'
drinks[56] = 'cocktails'
drinks[57] = 'barkeeper'
drink_to_idx = dict(zip(drinks, range(len(drinks))))

class Barschild:

    def __init__(self):
        self.time = utime.ticks_ms
        #self.sender = Sender()

    def set_pixel(self, num, color):
        np[num] = color
        np.write()

    def uniform_color(self, color):
        for i in range(NUM_PIXEL):
            np[i] = color
        np.write()

    def show_billboard(self):
        #TODO np durchgehen, vergleichen welche Elemente welcher Farbe entsprechen, output auf Farbe setzen
        print('TODO')

    def leer(self,drink):
        self.set_pixel(drink_to_idx[drink], RED)

    def voll(self,drink):
        #print(drink)
        print('set full: ', drink)
        self.set_pixel(drink_to_idx[drink], GREEN)

    def alles_voll(self):
        print('alles_voll')
        self.uniform_color((0,0,0))
        for self.drink in drink_to_idx.values():
            self.set_pixel(self.drink, GREEN)

    def alles_leer(self):
        print('alles_leer')
        self.uniform_color((0,0,0))
        for self.drink in drink_to_idx.values():
            self.set_pixel(self.drink, RED)

    def licht(self,color):
        for i in range(9,48):
            self.set_pixel(i, color)

    def lichtSchaden(self,color,times):
        while(True):
            modus = int(randint(0,10))
            print(modus)
            if modus == 0:
                self.lichtSchaden1(color,times)
            elif modus == 1:
                self.lichtSchaden2(color,times)
            elif modus == 2:
                self.lichtSchaden3(color,times)
            else:
                self.licht(WHITE)
            self.licht(WHITE)
            utime.sleep_ms(2000)

    def lichtSchaden1(self,color,times):
        for i in range(times):
            licht(WHITE)
            utime.sleep_ms(100)
            licht(BLACK)
            utime.sleep_ms(10)
            licht(WHITE)
            utime.sleep_ms(20)
            licht(BLACK)
            utime.sleep_ms(20)
            licht(WHITE)
            utime.sleep_ms(10)
            licht(BLACK)
            utime.sleep_ms(10)
            licht(WHITE)
            utime.sleep_ms(20)
            licht(BLACK)
            utime.sleep_ms(100)
            licht(WHITE)
            utime.sleep_ms(400)
            licht(BLACK)
            utime.sleep_ms(10)
        self.licht(WHITE)

    def lichtSchaden2(self,color,times):
        for i in range(times):
            licht(color)
            for i in range(4):
                utime.sleep_ms(50)
                licht(BLACK)
                utime.sleep_ms(50)
                licht(color)
            utime.sleep_ms(20)
            licht(STROBO)
            utime.sleep_ms(200)
            licht(BLACK)
            utime.sleep_ms(2000)
            licht(YELLOW)
            utime.sleep_ms(40)
            licht(STROBO)
            utime.sleep_ms(20)
            licht(BLACK)
            utime.sleep_ms(100)
        licht(WHITE)

    def lichtSchaden3(self,color,times):
        for j in range(15,17):
            for i in range(0,230,j):
                licht((i,i,i))
                utime.sleep_ms(30)
            licht(BLACK)
            utime.sleep_ms(randint(100,5000))
        licht(WHITE)

    def info(self):
        print('functions:')
        print("leer('bier')")
        print("voll('bier')")
        print("alles_leer()")
        print("licht(<color>)")
        print('alles_voll()\n')
        print('Die drinks die angeboten werden: ')
        print('special ,spezi, mate, shot, barkeeper, alkfrei, radler, brause, Barkeeper, cocktails')

    def strobo(color1 = STROBO, color2 = BLACK, times=20):
        print('start strobo')
        for i in range(times):
            barschild.licht(WHITE)
            utime.sleep_ms(40)
            barschild.licht(BLACK)
            utime.sleep_ms(80)
        barschild.licht(WHITE)

    def chase(self):
        uniform_color(BLACK)
        for i in range(10):
            #left side
            set_pixel(i+9,YELLOW)
            #right side
            set_pixel(8-i,YELLOW)
            utime.sleep_ms(200)

    def chaseOld(self):
        uniform_color(BLACK)
        for i in range(NUM_PIXEL):
            set_pixel(i,YELLOW)
            #set_pixel(i-1,BLACK)
            utime.sleep_ms(100)

    def rand(self):
        return int.from_bytes(uos.urandom(4), 'little')

    def randint(a, b):
        return (rand() % (b - a)) + a

    def choice(a):
        return a[rand() % len(a)]

    def sample(a, n):
        ret = []
        for i in range(n):
            randEl = choice(a)
            ret.append(randEl)
            a.remove(randEl)
        return ret

#class Sender():
#    def __init__(self):
#        self.np = neopixel.NeoPixel(machine.Pin(PIN), NUM_PIXEL)
#
#    def send(self, pixel_values):
#        for i in range(NUM_PIXEL):
#            self.neop[i] = pixel_values[i]
#        self.neop.write()

async def main(barschild):
    barschild.alles_voll()
    barschild.licht(WHITE)
    print('entering main loop: ')
    while True:
        await asyncio.sleep_ms(10)



class ApiHandler:
    def __init__(self, barschild):
        self.barschild = barschild
        file = open("Barschild.html")
        self.INDEX = str(file.read())
        file.close()

    def index(self):
        return self.INDEX

    def get(self, api_request):
        print("Der Apirequest ist angekommen: ")
        print(api_request)
        operation =  api_request['query_params'].get('operation', 'index')
        if 'strobo' == operation:
            self.barschild.strobo()
        elif 'voll' == operation:
            value = str(api_request['query_params']['value'])
            print("voll", value)
            self.barschild.voll(value)
            #self.chess.set_turn("white", time=value)
        elif 'leer' == operation:
            value = str(api_request['query_params']['value'])
            print("leer", value)
            self.barschild.leer(value)
            #self.chess.set_turn("white", time=value)
        elif 'restart' == operation:
            print("restart game")
            self.barschild.restart()
        elif operation == 'index':
            print("send webpage")
            return self.INDEX
        elif operation == 'hello':
            print("Hello World")
            return('''
            <!DOCTYPE html>
             <html>
              <header>
              <title> EasterEgg: </title>
              </header>
              <body> Hello  world </body>
              </html>''')

if __name__ == "__main__":
    barschild = Barschild()
    api_handler = http_api_handler.Handler([([''], ApiHandler(barschild))])
    loop = asyncio.get_event_loop()
    loop.create_task(main(barschild))
    server = uhttpd.Server([('/api', api_handler)])
    server.run()
