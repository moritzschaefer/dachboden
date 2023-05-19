import machine, utime


PIN_IDS = [2, 4, 12, 14]

PINS = []
for id in PIN_IDS:
    pin = machine.Pin(id, machine.Pin.OUT)
    PINS.append(pin)

def strobo():
    for pin in PINS:
        pin.on()
    utime.sleep_ms(20)
    for pin in PINS:
        pin.off()




def main():
    while True:
        for j in [5,20,40,100,200,500]:
            for i in range(10):
                strobo()
                utime.sleep_ms(j)



if __name__ == "__main__":
    main()



