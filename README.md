# Dachboden
In the Dachboden there are currently four microcontroller and two Linux projects.

## Microcontroller
The 32-bit microcontroller ESP8266 is used with the operating system [NodeMCU](https://de.wikipedia.org/wiki/NodeMCU) on which the Python3 environment [Micropython](https://github.com/micropython/micropython/ "Micropython") is installed.
Each microcontroller is communicates with the Open Sound Control (OSC) protocol.
The protocol is used so that the microcontroller can be controlled with the [QLC+](https://github.com/mcallegari/qlcplus "QLC+") program.
After flashing and installing micropython, the microcontroller gets assigned a static IP from the Fritzbox.
If the IP is known, [WEBREPL](https://github.com/micropython/webrepl "WEBREPL") can be used to access the microcontroller and a program can be transferred.

### Set up device
If there are tools or files missing, look at the well documentation https://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/network_basics.html

#### Flashing device
    $ esptool.py --port /dev/ttyUSB0 erase_fla
    $ esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 Downloads/esp8266-20180511-v1.9.4.bin

#### Setup wireless
    $ import webrepl_setup
    $ import network
    $ sta_if = network.WLAN(network.STA_IF)
    $ sta_if.active(True)
       #6 ets_task(4020f474, 28, 3fff93a8, 10)
    $ sta_if.connect('Incubator', 'Fl4mongo')
    $ sta_if.isconnected()
       True
    $ sta_if.ifconfig()
      ('192.168.178.124', '255.255.255.0', '192.168.178.1', '192.168.178.1')

#### Connect via WEBrepl

## Existing chips

### Ambiente
The Ambience project is there to illuminate simple LED strips in the Dachboden.
At the moment there is only one mode installed to illuminate the whole strip in any colour.

### BigEye
The BigEye project is to control LED stripes in large round glass containers.
The source code differs from Ambiente in that there is a mode that can be used to control half of the LEDS in one colour.

### Sternenhimmel
The Sternenhimmel project is to control an LED strip.
There are three modes in the code:
1. All LEDs light up in one color
2. All LEDs pulsate in a random color
3. Each individual LED can be addressed individually

### BarGame
The BarGame project is a reaction game at the bar.
In the game there are two screens on which different symbols are displayed.
At the beginning of the game a target symbol is displayed. 
If the symbol is displayed on the screen again, the player who presses the screen first wins.

## Raspberry Pi
### Schuettelstab
The Schüttelstab project consists of a very fast LED Stripe.
By a fast shaking of the head an image is generated.
The image can be changed by logging in to the WLAN of the shaking stick (Jote..) and then going to any page.
You will then be automatically forwarded to the Raspberry PI page.

To connect to Raspberry PI 

   ssh pi@192.168.42.1
   
Password: raspberry

### Kickercam
The Kickercam transmits a live transmission of the Kicker to a screen.
The corresponding program is written with Python and runs on a Raspberry PI or on a laptop.
The laptop is more advantageous, because the calculation is carried out fast enough there.
In addition to the live transmission, the goal shot is detected.

## WebREPL

Run

    git submodule init && git submodule update

to initialize the webrepl directory access. Use

    python -m http.server

in the webrepl dir to access webrepl

## IPs

- 192.168.178.170: ESP-239C3D ambiente
- 192.168.178.73: ESP-0213EF sternenhimmel
- 192.168.178.151: ESP-239663 bigeye NOT!!!!
- ...: ESP_E1A34B stageback

### flashed but empty

- 192.168.178.151 free
- 192.168.178.124 free


REPL Password: incubator
