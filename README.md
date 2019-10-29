# Dachboden
In the Dachboden there are currently four microcontroller and two Linux projects.

## Microcontroller
The 32-bit microcontroller ESP8266 is used with the operating system [NodeMCU](https://de.wikipedia.org/wiki/NodeMCU) on which the Python3 environment [Micropython](https://github.com/micropython/micropython/ "Micropython") is installed.
Each microcontroller is communicates with the Open Sound Control (OSC) protocol.
The protocol is used so that the microcontroller can be controlled with the [QLC+](https://github.com/mcallegari/qlcplus "QLC+") program.
After flashing and installing micropython, the microcontroller gets assigned a static IP from the Fritzbox.
If the IP is known, [WEBREPL](https://github.com/micropython/webrepl "WEBREPL") (Read-eval-print loop) can be used to access the microcontroller and a program can be transferred.

The main program is called main and is started automatically after the restart.
All files are located in the root folder. If the microcontroller outputs strange characters, either the baud rate is set incorrectly or a program is running and must be terminated with CTRL+C.

If you are using Mac OS High Sierra, the [driver](https://github.com/esp8266/Arduino/issues/732 "driver") must be installed.

### Set up device
If there are tools or files missing, look at the well documentation https://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/network_basics.html

#### Flashing device
Remove memory in Flash.

    $ esptool.py --port /dev/ttyUSB0 erase_flash

Download firmware from [MicroPython downloads page](http://micropython.org/download#esp8266) and write firmware.

    $ esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 Downloads/esp8266-20180511-v1.9.4.bin

#### REPL over the serial port
Connect via a serial port to the microcontroller, under Linux e.g.

    $ picocom /dev/ttyUSB0 -b115200

#### Setup wireless
Open webrepl setup and set password for the microcontroller.

    $ import webrepl_setup

At this point, an input must happen.

    $ import network
    $ sta_if = network.WLAN(network.STA_IF)
    $ sta_if.active(True)
       #6 ets_task(4020f474, 28, 3fff93a8, 10)
    $ sta_if.connect('Incubator', 'Fl4mongo')
    $ sta_if.isconnected()
       True
    $ sta_if.ifconfig()
      ('192.168.178.124', '255.255.255.0', '192.168.178.1', '192.168.178.1')

For keep settings after restart, just do:

    $ import machine
    $ machine.reset()

### WebREPL

Run

    git submodule init && git submodule update

to initialize the webrepl directory access. Use

    python -m http.server

in the webrepl dir to access webrepl

REPL Password: incubator

## Sending Files over commandline

	$ python webrepl_cli.py ../PROJECT/main.py 192.168.178.IP:/ -p "incubator

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

Password: raspberry or Raspberry

### Kickercam
The Kickercam transmits a live transmission of the Kicker to a screen.
The corresponding program is written with Python and runs on a Raspberry PI or on a laptop.
The laptop is more advantageous, because the calculation is carried out fast enough there.
In addition to the live transmission, the goal shot is detected.

### ToiletDisko
Raspberry for controlling neopixels and audio on the disco toilet.
[A good guide](https://learn.adafruit.com/neopixels-on-raspberry-pi/software) to control the neopixels via the Raspberry Pi.

## IPs

- 192.168.178.170: ESP-239C3D ambiente
- 192.168.178.73:  ESP-0213EF sternenhimmel
- 192.168.178.151: ESP-239663 bigeye NOT!!!!
- 192.168.178.191: ArcadeKicker
- 192.168.178.177: DachbodenSchild
- ...............: ESP_E1A34B stageback
- 192.168.178.191: //TODO Moritz trag was ein
- 192.168.178.185: schach
- 192.168.178.80:  barschild
- 192.168.178.78:  ESP-E1A3E4 lasercannon
- 192.168.178.79:  ESP-E1A287 dystocity
- 192.168.178.191: ESP-E1A166 arcadekicker

183, need to be added here!


### flashed but empty

- 192.168.178.151 free
- 192.168.178.124 free


REPL Password: incubator

## Dancefloor-Beleuchtung mit E1.31 DMX

Im Gegensatz zu eigenständigen Installationen, wie dem Kicker oder dem
Schachbrett, sollten die Projekte, die als Dancefloor-Beleuchtung gedacht sind,
möglichst zentral über das Lichtpult bzw. den Lichtrechner gesteuert werden
können. Dort wird die Lichtsoftware QLC+ eingesetzt. Die Lichter laufen wie gehabt
auf ESP32- oder ESP8266-Basis, die Datenübertragung findet also über WLAN statt.
Deshalb erfolgt die Einbindung in QLC+ über das E1.31-Protokoll, welches
dazu gedacht ist DMX-Daten über IP-Netzwerke zu übertragen.

Eine zeitkritische Anwendung wie DMX-Lichtkontrolle über WLAN zu betreiben ist
allgemein keine gute Idee, da wir es aber nun mal aus historischen Gründen so
machen, gibt es für die Geräte immerhin ein eigenes WLAN-Netz (über den schwarzen
TP-Link am Lichthaus, der zu den meisten Geräten Sichtkontakt hat). Es hört auf
den Namen "Fischnetz" mit dem üblichen Passwort und soll *exklusiv* für die
DMX-Steuerung der Lichttechnik genutzt werden.

Die Geräte hören dabei alle auf das DMX Universum 5, so dass man auf dem Lichtrechner
sich nur zum "Fischnetz" verbinden und den Output für Universe 5 auf E1.31 stellen muss.

Es handelt sich bei den Geräten z.B. um den Stroboter, die Quallen und das UV-Strobo.
Die Firmware setzt im Gegensatz zu den meisten anderen Projekten nicht auf Micropython, 
sondern auf den Arduino Cores der jeweiligen Controller auf (siehe z.B. den Code
für den Stroboter).

Alle belegten Kanäle im Universe 5 sind hier aufgeführt
(und werden hoffentlich aktualisiert):

| Kanal         | Gerät           |
| ------------- |:-------------:|
| 1 - 30    | Masterqualle |
| 31 - 36   | Qualle 1  |
| 37 - 42   | Qualle 2  |
| 43 - 48   | Qualle 3  |
| 48 - 54   | Qualle 4  |
| 55 - 60   | Qualle 5  |
| 61 - 66   | Qualle 6  |
| 67 - 72   | Qualle 7  |
| 73 - 78   | Qualle 8  |
| 78 - 84   | Qualle 9  |
| 85 - 90   | Qualle 10 |
| 91 - 96   | Qualle 11 |
| 97 - 102  | Qualle 12 |
| 103 - 108 | Qualle 13 |
| 108 - 114 | Qualle 14 |
| 115 - 120 | Qualle 15 |
| 141 - 145 | UV-Strobo |
| 151 - 158 | Stroboter |
| 161 - 165 | Lichtpeitsche |
| 171 - 175 | Friedrich2 |




