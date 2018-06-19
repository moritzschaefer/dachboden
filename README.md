# dachboden
Each microcontroller is controlled by the Open Sound Control (OSC) protocol.
The protocol is used so that Sylwan can control the microcontroller with its QLC+ program.
To do this, each microcontroller must first be flashed with [Micrpython](https://github.com/micropython/micropython/ "Micropython").
After flashing, the microcontroller is assigned a static IP with the Fritzbox.
If the IP is known, [WEBREPL](https://github.com/micropython/webrepl "WEBREPL") can be used to access the microcontroller and a program can be transferred.

## IPs

- 192.168.178.170: ESP-239C3D ambiente
- 192.168.178.73: ESP-0213EF sternenhimmel


REPL Password: incubator
