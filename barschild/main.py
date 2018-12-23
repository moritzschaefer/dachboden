import machine, neopixel, time

PIN = 2
NUM_PIXEL = 19
INTENSITY = 80

RED = (INTENSITY, 0, 0)
GREEN = (3, 50, 0)
YELLOW = (30, 30, 0)

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
    alles_da()
    leer('mexikaner')
    leer('j koffeinfrei')

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

if __name__ == "__main__":
    main()
