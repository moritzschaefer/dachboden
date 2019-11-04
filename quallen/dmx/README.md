# What's in here?

Arduino sketch for esp32 and esp8266, to control the quallen via E1.31 DMX over 
Ethernet. Works with QLC+.

# Requirements (in parentheses the version that was used, newer versions *can* also work)

* Arduino IDE (1.8.9)
* Arduinoe Core for ESP32 (git master as of 2019-08-01): https://github.com/espressif/arduino-esp32 and/or Arduino Core for ESP8266 (2.5.2): https://github.com/esp8266/Arduino
* NeoPixelBus (2.5.0): https://github.com/Makuna/NeoPixelBus or via library manager
* WifiManager (git **development** branch as of 2019-08-31): https://github.com/tzapu/WiFiManager
* ESPAsyncE131 (git master as of 2019-01-06): https://github.com/forkineye/ESPAsyncE131
* ESP8266 only: ESPAsyncUDP (git master as of 2017-11-21): https://github.com/me-no-dev/ESPAsyncUDP
* ArduinoJson (5.13.5): via library manager

# Hints

* Each qualle has 6 channels:

| Channel       | Function      | 
| ------------- |:-------------:|
| 1  | Dimmer |
| 2  | Red value |
| 3  | Green value |
| 4  | Blue value |
| 5  | Strobe frequency (0-25 Hz, 0 means on)
| 6  | Strobe on duration (0-255 ms) |

* quallen go to GPIO 5 on esp32 and RX on esp8266 (when you set a different pin 
it is ignored on esp8266).

* You don't need to change the source. The settings (AP name and pwd,
DMX universe, channel offset, led counts etc) are all done with the
web config ui

* connect GPIO 4 and GND on poweron to force the AP mode and config webserver.
Should automatically run on first boot or when no wifi available.

# TODO

* ~~OTA Updates~~
* Trigger web config without the need to connect some pin to ground
