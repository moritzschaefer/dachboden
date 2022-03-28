from machine import Pin, PWM, ADC
import time

# esptool.py --port /dev/tty.usbserial-210 --baud 460800 erase_flash
# esptool.py --port /dev/tty.usbserial-210 --baud 460800 write_flash --flash_size=detect 0 esp8266-20191220-v1.12.bin
# picocom /dev/tty.usbserial-210 -b115200
#  import webrepl_setup
#
#  import network
#  sta_if = network.WLAN(network.STA_IF)
#  sta_if.active(True)
#  sta_if.connect('dachboden', 'epicattic')
#  sta_if.isconnected()
#  sta_if.ifconfig()

# 192.168.0.146

# python ../webrepl/webrepl_cli.py main.py 192.168.0.146:/ -p "incubator"

# Limit the motor to max. 400mA, see data sheet of a similar motor https://www.sparkfun.com/products/10551.

resetPin = Pin(5, Pin.OUT) # This is PIN D1
motorPin = Pin(4, Pin.OUT) # This is PIN D2
sleepPin = Pin(0, Pin.OUT) # This is PIN D3

# https://randomnerdtutorials.com/esp32-esp8266-analog-readings-micropython/
potentioMeter = ADC(0) # This is PIN A0

# potentioMeter.read() returns values from 0 to 1024

ledPin = Pin(14, Pin.OUT)

resetPin.value(1)
sleepPin.value(1)

pwmMotor = PWM(motorPin)

# Unterlegescheibe

# Frequency must start low for the device to start moving
frequency = 5
endFrequency = 700
duty = 512

while True:
    if (frequency < endFrequency):
        pwmMotor.freq(frequency)
        pwmMotor.duty(duty)

        frequency = min(frequency + 3, endFrequency)
        time.sleep_ms(250)
    else:
        pot_value = potentioMeter.read()
        sleep_time = int(10 + (1024 - pot_value) * 100)

        ledPin.value(1)
        time.sleep_us(25)
        ledPin.value(0)
        time.sleep_us(sleep_time)
