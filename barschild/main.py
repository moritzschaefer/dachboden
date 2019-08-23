import machine, neopixel, time
import utime #for strobo

PIN = 2
NUM_PIXEL = 19
INTENSITY = 40

RED = (16, 0, 0)
GREEN = (1, 8, 0)
YELLOW = (15, 15, 0)
WHITE = (50, 50, 50)
BLACK = (0, 0, 0)

np = neopixel.NeoPixel(machine.Pin(PIN), NUM_PIXEL)

def set_pixel(num, color):
    np[num] = color
    np.write()

def uniform_color(color):
    for i in range(NUM_PIXEL):
        np[i] = color
    np.write()

def show_billboard():
    #TODO np durchgehen, vergleichen welche Elemente welcher Farbe entsprechen, output auf Farbe setzen
    print('TODO')

drinks = ['dachschaden',
          'fruechtchen',
          'wodka mate',
          'cosmopolitan',
          'moscow mule',
          'tequila sunrise',
          'j koffeinfrei',
          'jetraenk',
          'radler',
          'bier',
          'mate',
          'cola',
          'mojito',
          'gin tonic',
          'sex on the beach',
          'cuba libre',
          'pfeffi',
          'mexikaner',
          'kolja']

cocktails = ['wodka mate',
          'cosmopolitan',
          'moscow mule',
          'tequila sunrise',
          'mojito',
          'gin tonic',
          'sex on the beach',
          'cuba libre']

drink_to_idx = dict(zip(drinks, range(len(drinks))))

def leer(drink):
    set_pixel(drink_to_idx[drink], RED)

def wieder_da(drink):
    set_pixel(drink_to_idx[drink], GREEN)

def cocktails_leer():
    leer('cocktails')

def cocktails_wieder_da():
    wieder_da('cocktails')

def alles_da():
    uniform_color((0,0,0))
    for drink in drink_to_idx.values():
        set_pixel(drink, GREEN)

def alles_leer():
    uniform_color((0,0,0))
    for drink in drink_to_idx.values():
        set_pixel(drink, RED)

def main():
    alles_leer()
    wieder_da('bier')
    wieder_da('mate')
    #leer('mexikaner')
    #leer('j koffeinfrei')

def info():
    print('functions:\n')
    print("leer('Bier')\n")
    print("voll('Bier')\n")
    print('alles_leer()\n')
    print('alles_voll()\n')
    print('cocktails_leer()\n')
    print('cocktails_voll()\n')
    print('Die drinks die angeboten werden: \n')
    for drink in drinks:
        print(drink)

def strobo(color1=WHITE, color2=BLACK, times=200):
    for i in range(times):
        uniform_color(color1)
        utime.sleep_ms(40)
        uniform_color(color2)
        utime.sleep_ms(80)

def chase():
    uniform_color(BLACK)
    for i in range(10):
        #left side
        set_pixel(i+9,YELLOW)
        #right side
        set_pixel(8-i,YELLOW)
        utime.sleep_ms(200)

def chaseOld():
    uniform_color(BLACK)
    for i in range(NUM_PIXEL):
        set_pixel(i,YELLOW)
        #set_pixel(i-1,BLACK)
        utime.sleep_ms(100)

if __name__ == "__main__":
    main()
