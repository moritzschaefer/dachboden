# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('Incubator', 'Fl4mongo')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

do_connect()
import webrepl
"""
sta_if = network.WLAN(network.STA_IF)

ap_if =network.WLAN(network.AP_IF)
ap_if.active(True)

x = 0
while not sta_if.isconnected() and x < 5:
    sta_if.active(True)
    sta_if.connect('Incubator', 'Fl4mongo')
    time.sleep(1)
    x += 1
"""

webrepl.start()
