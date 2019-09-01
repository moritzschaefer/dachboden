# What's in here?

Arduino sketch for esp32, to control the quallen via E1.31 DMX over Ethernet.
Works with QLC+. Untested on esp8266, but should work. Requires specific versions
of some libs. More docs later ;)

# Hints
quallen go to GPIO 5.

You only need to setup AP_NAME and AP_PWD in the source. The rest (wifi, 
led counts for up to 5 quallen and dmx settings) is configured 
with the web config ui.

connect GPIO 4 and GND on poweron to force the AP mode and config webserver.
Should automatically run on first boot or when no wifi available.
