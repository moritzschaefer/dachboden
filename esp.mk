index.html.min: index.html
	html-minifier --remove-comments --collapse-whitespace --minify-js true index.html > index.html.min
	../webrepl/webrepl_cli.py -p incubator index.html.min $(IP):/index.html ; \

.transfered: *.py
	for f in $?; do \
		../webrepl/webrepl_cli.py -p incubator $$f $(IP):/ ; \
	done
	touch .transfered
	echo "\x03\x04" > /dev/ttyUSB0

flash_esp32:
	wget "http://micropython.org/resources/firmware/esp32-idf3-20190529-v1.11.bin"
	esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
	esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-idf3-20190529-v1.11.bin

flash_esp8266:
	wget "http://micropython.org/resources/firmware/esp8266-20190529-v1.11.bin"
	esptool.py --chip esp8266 --port /dev/ttyUSB0 erase_flash
	esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 esp8266-20190529-v1.11.bin
