# What's in here?

Control software for the quallens to be run on a Linux PC (or maybe Raspberry PI in the future?). Can set current mode and misc settings on the quallens via udp packets.
Uses [aubio](https://aubio.org/) for live beat detection from a line in signal to send blink commands to the quallens in the blinky modes. Killer-feature: Can send the strobo command.

# Dependencies
written in python, uses
[aubio python bindings](https://aubio.org/download) for beat detection
[pyaudio](http://people.csail.mit.edu/hubert/pyaudio/) for record and playback of audio
numpy because aubio requires it

# Hints
The program has no way to know the state of the quallens (mode, max_brightness, strobo_duration, ...) on startup. So first thing you do is set them all to the desired values.

if you set USE_JACK=True in the code, then the jack sound server will be used. Otherwise
the default ALSA device will be used.

Keyboard bindings are listed in the bottom row of the beautiful curses ui.
