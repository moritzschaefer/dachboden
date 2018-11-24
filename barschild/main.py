import machine, neopixel, time

PIN = 2
NUM_PIXEL = 19
INTENSITY = 80

RED = (INTENSITY, 0, 0)
GREEN = (3, 50, 0)

np = neopixel.NeoPixel(machine.Pin(PIN), NUM_PIXEL)

def set_pixel(num, color):
    np[num] = color
    np.write()

def uniform_color(color):
    for i in range(NUM_PIXEL):
        np[i] = color
    np.write()

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

drink_to_idx = dict(zip(drinks, range(len(drinks))))

def leer(drink):
    set_pixel(drink_to_idx[drink], RED)

def wieder_da(drink):
    set_pixel(drink_to_idx[drink], GREEN)

def alles_da():
    uniform_color((0,0,0))
    for drink in drink_to_idx.values():
        set_pixel(drink, GREEN)

def alles_leer():
    uniform_color((0,0,0))
    for drink in drink_to_idx.values():
        set_pixel(drink, RED)

def main():
    alles_da()        

def info():
    print('functions:\n')
    print('leer(drink)')
    print('wieder_da(drink)')
    print('alles_da()')
    print('alles_leer()\n')
    for drink in drinks:
        print(drink)

if __name__ == "__main__":
    main()
