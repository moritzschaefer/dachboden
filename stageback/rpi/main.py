import RPi.GPIO as GPIO
import time
import socket
import array
# 1   8  14  21
#   5  12  18
# 2   9  15  22
#   6  13  19
# 3  10  16  23
#   7  --  20
# 4  11  17  24

PINS = list(range(2, 26))


def callback(universe, channel, value):  # channel is 1-based indexed
    print((universe, channel, value))
    if value == 0.0:
        GPIO.output(PINS[channel], GPIO.HIGH)
    else:
        GPIO.output(PINS[channel], GPIO.LOW)


def main():
    # rclk: D1=GPIO5 Pin
    GPIO.setmode(GPIO.BCM)
    for pin in PINS:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)  # disable (low-active..)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('0.0.0.0', 9000)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)
    sock.settimeout(0.1)
    i = 0
    while True:
        try:
            data, _ = sock.recvfrom(64)
        except OSError:  # timeout!!
            GPIO.output(PINS[i-1], GPIO.HIGH)
            GPIO.output(PINS[i], GPIO.LOW)

            time.sleep(0.3)
            print('Set shift register to {}'.format(i))
            i = (i+1) % 24
        else:
            break  # go out of the for loop!

    sock.settimeout(None)

    try:
        while True:
            universe_end = data.find(b'/', 1)
            universe = int(data[1:universe_end])
            channel_end = data.find(b'\x00')
            channel = int(data[universe_end+5:channel_end])
            value = bytearray()
            value.append(data[-1])
            value.append(data[-2])
            value.append(data[-3])
            value.append(data[-4])
            value = array.array('f', value)[0]
            callback(universe, channel, value)
            data, _ = sock.recvfrom(64)
    finally:
        sock.close()


if __name__ == '__main__':
    main()
