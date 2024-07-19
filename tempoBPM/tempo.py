import board
import neopixel
from rpi_ws281x import PixelStrip, Color
from gpiozero import LED, Button
from time import time, sleep
from threading import Thread
import tm1637

# LED strip configuration
LED_COUNT = 10         # Number of LED pixels.
LED_PIN = 18           # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000   # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10           # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255   # Set to 0 for darkest and 255 for brightest
LED_INVERT = False     # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0

# Colors
DIM_RED = Color(50, 0, 0)      # Dim red color
YELLOW = Color(255, 255, 0)    # Yellow color for progress
BRIGHT_YELLOW = Color(255, 255, 50)  # Bright yellow color for the last LED
GREEN = Color(0, 255, 0)       # Green color for completion

# Create PixelStrip object with appropriate configuration
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# Initialize LED on GPIO 22 and Button on GPIO 18
led = LED(22)
button = Button(18)
tm = tm1637.TM1637(clk=6, dio=16)

# Initialize variables to store timestamps and BPM calculation
timestamps = []
bpm = 0
last_tap_time = 0
last_bpm = 0
bpm_stable_start_time = 0
bpm_stable = False
progress = 0
all_yellow_start_time = 0  # Time when all LEDs turned yellow
all_yellow = False  # Flag to check if all LEDs have been yellow for 3 seconds
transition_to_green = False  # Flag to indicate transition to green

def set_progress(strip, progress):
    """Set the progress bar on the LED strip.
    
    Args:
        strip (PixelStrip): The LED strip object.
        progress (int): Number of LEDs to light up in yellow.
    """
    global all_yellow_start_time, all_yellow, transition_to_green

    if progress == strip.numPixels():
        if not all_yellow:
            all_yellow_start_time = time()
            all_yellow = True
        elif time() - all_yellow_start_time >= 3:
            transition_to_green = True
            all_yellow = False  # Reset flag
    else:
        all_yellow = False
        all_yellow_start_time = 0

    if transition_to_green:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, GREEN)
    else:
        for i in range(strip.numPixels()):
            if i < progress - 1:
                strip.setPixelColor(i, YELLOW)  # Normal yellow for progress
            elif i == progress - 1:
                strip.setPixelColor(i, BRIGHT_YELLOW)  # Bright yellow for the last LED
            else:
                strip.setPixelColor(i, DIM_RED)  # Dim red for the rest

    strip.show()

    if transition_to_green:
        tm.scroll("TASK COMPLETED")
        # Reset the transition flag after displaying the message
        transition_to_green = False

def calculate_bpm():
    global bpm, last_bpm, bpm_stable, bpm_stable_start_time, progress
    if len(timestamps) > 1:
        # Calculate time differences between consecutive button presses
        time_diffs = [timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))]
        avg_time_diff = sum(time_diffs) / len(time_diffs)
        bpm = 60.0 / avg_time_diff

        # Tolerance of ±2 BPM
        if abs(bpm - last_bpm) <= 2:
            if not bpm_stable:
                bpm_stable_start_time = time()
                bpm_stable = True
            progress = min(progress + 1, LED_COUNT)  # Increment progress by 1 LED, up to the maximum count
        else:
            bpm_stable = False
            bpm_stable_start_time = 0
            progress = max(progress - 1, 0)  # Decrement progress by 1 LED, down to 0
        last_bpm = bpm
    else:
        bpm = 0
        bpm_stable = False

def on_button_pressed():
    global timestamps, last_tap_time
    # Record current time when button is pressed
    current_time = time()
    #print("pressed")
    timestamps.append(current_time)
    last_tap_time = current_time
    # Keep only the last 10 timestamps for BPM calculation
    if len(timestamps) > 10:
        timestamps.pop(0)
    # Light the LED
    led.on()
    sleep(0.1)  # LED stays on for a short period
    led.off()
    calculate_bpm()
    set_progress(strip, progress)

def display_bpm():
    global bpm, progress
    while True:
        current_time = time()
        # If no one taps during 4 secs, the bpm is set back to 0 and LEDs turn red
        if current_time - last_tap_time > 4:
            bpm = 0
            progress = 0
            set_progress(strip, progress)
        if bpm > 0 and not bpm_stable:
            tm.number(int(bpm))
        elif bpm == 0:
            tm.number(0)
        sleep(1)

# Bind the button press event to the handler function
button.when_pressed = on_button_pressed

# Start a thread to continuously print BPM
bpm_thread = Thread(target=display_bpm)
bpm_thread.daemon = True
bpm_thread.start()

# Keep the program running
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    set_progress(strip, 0)  # Turn off LED strip (all red)
    print("Program terminated")
