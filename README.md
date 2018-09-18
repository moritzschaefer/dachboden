# dachboden
Each microcontroller is controlled by the Open Sound Control (OSC) protocol.
The protocol is used so that Sylwan can control the microcontroller with the [QLC+](https://github.com/mcallegari/qlcplus "QLC+") program.
To do this, each microcontroller must first be flashed with [Micropython](https://github.com/micropython/micropython/ "Micropython").
After flashing, the microcontroller is assigned a static IP with the Fritzbox.
If the IP is known, [WEBREPL](https://github.com/micropython/webrepl "WEBREPL") can be used to access the microcontroller and a program can be transferred.

## WebREPL

Run

    git submodule init && git submodule update

to initialize the webrepl directory access. Use

    python -m http.server

in the webrepl dir to access webrepl

## IPs

- 192.168.178.170: ESP-239C3D ambiente
- 192.168.178.73: ESP-0213EF sternenhimmel
- 192.168.178.151: ESP-239663 bigeye
- ...: ESP_E1A34B stageback


REPL Password: incubator
