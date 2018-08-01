import machine
import micropython
import socket
import array

# Channels: '0123'
# 0 green
# 1 red
# 2 blue
# 3 white
pins = [machine.Pin(v, machine.Pin.OUT, value=1) for v in [0,2,4,5]]
pwms = [machine.PWM(pin, freq=1000, duty=512) for pin in pins]

def osc_listen(callback):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('0.0.0.0', 9000)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)
    try:
        while True:
            data, _ = sock.recvfrom(64)
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
            print(data[-4:])
            callback(universe, channel, value)
    finally:
        sock.close()

def callback(universe, channel, value):
    pwms[channel].duty(int(value*1023))


if __name__ == '__main__':
    osc_listen(callback)

