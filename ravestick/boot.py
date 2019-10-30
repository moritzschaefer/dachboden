# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

import esp
import webrepl

esp.osdebug(None)
def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('Morispot', 'moritzsch')
        while not sta_if.isconnected():
            pass
        
    print('network config:', sta_if.ifconfig())

do_connect()

webrepl.start()
