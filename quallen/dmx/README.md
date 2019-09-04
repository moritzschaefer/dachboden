# What's in here?

Arduino sketch for esp32 and esp8266, to control the quallen via E1.31 DMX over 
Ethernet. Works with QLC+. Requires specific versions
of some libs. More docs later ;)

# Hints
quallen go to GPIO 5 on esp32 and RX on esp8266 (when you set a different pin 
it is ignored on esp8266).

You only need to setup AP_NAME and AP_PWD in the source. The rest (wifi,
led counts for up to 5 quallen and dmx settings) is configured 
with the web config ui.

connect GPIO 4 and GND on poweron to force the AP mode and config webserver.
Should automatically run on first boot or when no wifi available.
