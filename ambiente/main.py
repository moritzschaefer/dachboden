from umqtt.simple import MQTTClient
from machine import Pin
import ubinascii
import machine
import micropython

# Channels: '0123'
# 0 green
# 1 red
# 2 blue
# 3 white
pins = [Pin(v, Pin.OUT, value=1) for v in [0,2,4,5]]
pwms = [machine.PWM(pin, freq=1000, duty=512) for pin in pins]


# Default MQTT server to connect to
SERVER = "optilux"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC = b"ambiente"

state = 0

def sub_cb(topic, msg):
    print((topic, msg))
    for i in range(4):
        pwms[i].duty(msg[i]*4)


def main(server=SERVER):
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
