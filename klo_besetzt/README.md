firmware for the micro-controller taking care of showing if the bathroom is free or occupied.

setting
=======

in the Dachboden there is a sign over the bathroom's door to indicate if the bathroom is occupied.
by pressing on a button you could switch between lighting the left side of the sign marked "frei" (e.g. free) using green light, or the right side marked "besetzt" (e.g. occupied) using red light.

history
=======

but you had to manually press on the button to switch the light to the right status.
plus the button was on the outside of the bathroom.

modification
============

I wanted the status update to be automatic.
for that I embedded a micro-switch in the wooden frame behind the strike plate.
this would detect if the lock is engaged, indicating someone is using the bathroom.
I replaced the button connections to the micro-controller board with the one from the switch.
sadly this modification was not enough.
the firmware would change the state (e.g. which side of the sign is lighted) every time the switch gets pressed.
thus the status only changes once when the door gets locked.
but to work as intended it should also change when the door get unlocked.

board
=====

since I did not have the firmware for the board controlling the light (and no one knew where it was), I had to reverse the setup and rewrite it.
the board used is an Arduino Nano.
the light used are RGBW LEDs controlled by one data line.
I figured they would be SK2812 LEDs (uses the same protocol as WS2812b with a 4th byte for additional white component).
the board had the ATmega328P with the old Arduino bootloader.
this allowed me to dump the existing firmware (see firmware_old.bin), and flash a new one.

firmware
========

to program the firmware I used:
- Arduino IDE v1.8.9
- Adafruit NeoPixel by Adafruit v1.2.5 (available in library manager)

the micro-switch is connected on pin 3 and 4.
pin 4 drives the signal low.
pin 3 is an input pulled high.
when pin 3 is low it means the switch is closed, e.g. the door is locked.
pin 2 sends the data to the LEDs.
there are 32 RGBW LEDs:
- the first 16 RGBW LEDs are on the left side of the sign and should light green when the bathroom is free (e.g. door is unlocked)
- the last 16 RGBW LEDs are on the right side of the sign and should light red when the bathroom is occupied (e.g. door is locked)

I included the output firmware binary as klo_besetzt.hex.
