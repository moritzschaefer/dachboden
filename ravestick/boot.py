# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import network
import webrepl
import time

sta_if = network.WLAN(network.STA_IF)
x = 0
while not sta_if.isconnected() and x < 5:
    sta_if.active(True)
    sta_if.connect('Incubator', 'Fl4mongo')
    time.sleep(1)
    x += 1


webrepl.start()
