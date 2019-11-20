# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
import gc

import network
from utime import sleep_ms

sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)
if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect('Incubator', 'Fl4mongo')
    i = 0
    while not sta_if.isconnected():
        sleep_ms(10)
        i +=1
        if(i>1000):
            break

ap_if.active(False)

print('network config sta_if:', sta_if.active())
print('network config ap_if:', ap_if.active())
print('network config:', sta_if.ifconfig())

import webrepl
webrepl.start()
gc.collect()
