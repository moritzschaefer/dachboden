from umqtt.simple import MQTTClient
from machine import Pin
import ubinascii
import machine
import micropython
import neopixel

leds = neopixel.NeoPixel(machine.Pin(5, machine.Pin.OUT), 27)
 
# Default MQTT server to connect to
SERVER = "optilux"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC = b"bigeye"

state = 0

def sub_cb(topic, msg):
    print((topic, msg))
    for i in range(27):
        leds[i] = (msg[i*3], msg[i*3+1], msg[i*3+2])
    leds.write()
        

def main(server=SERVER):
    #default light on
    for i in range(27):
        leds[i] = (256,150,150)
    leds.write()

    c = MQTTClient(CLIENT_ID, server)
    # Subscribed messages will be delivered to this callback
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(TOPIC)
    print("Connected to %s, subscribed to %s topic" % (server, TOPIC))

    try:
        while 1:
            #micropython.mem_info()
            c.wait_msg()
    finally:
        c.disconnect()

if __name__ == '__main__':
    main()
