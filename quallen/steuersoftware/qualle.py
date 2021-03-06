#!/usr/bin/env python3

import sys
import socket
import os
import curses
from curses.textpad import Textbox
import time
from subprocess import check_output, CalledProcessError, STDOUT, DEVNULL, PIPE, Popen
from datetime import datetime, timedelta
import threading
from collections import OrderedDict
import re
import socket
import contextlib
import aubio
import numpy as np
import pyaudio

screen = None
quallen = None
server = None

mode_ctime = None
mode_prev = None
strobo_duration = 1
mode = "DEFAULT"
mode_prev = "DEFAULT"
ping_time = datetime.now()

class Quallen(object):
    def __init__(self):
        self.quallen = [1, 2, 3]
        self.quallen_index = 0

    def get_next_qualle(self):
        global screen
        qualle = self.quallen[self.quallen_index]
        self.quallen_index = (self.quallen_index + 1) % len(self.quallen)
        #  screen.log('beat single on qualle ' + str(qualle))
        return qualle

USE_JACK = True

class Color(object):
    red = None
    green = None
    blue = None
    mainwin = None
    logwin = None
    helpwin = None


@contextlib.contextmanager
def ignore_stderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)

@contextlib.contextmanager
def ignore_stdout():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stdout = os.dup(1)
    sys.stdout.flush()
    os.dup2(devnull, 1)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stdout, 1)
        os.close(old_stdout)

class BeatDetection(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.win_s = 2048               # fft size
        #  self.hop_s = 512
        self.hop_s = 512 
        #  self.samplerate = 44100
        self.samplerate = 48000
        self.tempo = aubio.tempo("default", self.win_s, self.hop_s, self.samplerate)
        self.click = 0.7 * np.sin(2. * np.pi * np.arange(self.hop_s) / self.hop_s * self.samplerate / 3000.)

        # suppress Jack and ALSA error messages on Linux.
        with ignore_stdout():
            with ignore_stderr():
                p = pyaudio.PyAudio()

        self.clicks = 1

        outdev = None
        indev = None

        if USE_JACK:
            outdev =  p.get_host_api_info_by_type(pyaudio.paJACK)['defaultOutputDevice']
            indev =  p.get_host_api_info_by_type(pyaudio.paJACK)['defaultInputDevice']

        pyaudio_format = pyaudio.paFloat32
        frames_per_buffer = self.hop_s
        n_channels = 1

        self.stream = p.open(format=pyaudio_format, channels=n_channels, rate=self.samplerate,
        output_device_index=outdev,
        input_device_index=indev,
        output=True, input=True,
        frames_per_buffer=frames_per_buffer,
        stream_callback=self.pyaudio_callback)

        # start pyaudio stream
        self.stream.start_stream()

    def pyaudio_callback(self, _in_data, _frame_count, _time_info, _status):
        global screen, mode, quallen, server
        #  samples, read = a_source()
        read = self.hop_s
        #  samples = np.fromstring(_in_data, dtype=np.float32)
        samples = np.copy(np.frombuffer(_in_data, dtype=np.float32))

        is_beat = self.tempo(samples)
        if is_beat:
            if (mode == "BEAT SINGLE"):
                try:
                    qualle = quallen.get_next_qualle()

                    qualle_idx = str.encode(str(qualle))
                    server.send_to_all(b'flash ' + qualle_idx)
                except Exception as e:
                    screen.log(e)

            elif mode == "BEAT ALL":
                server.send_to_all(b'flash 0')
            samples += self.click

            screen.setline_noblock(1, "cpu load:  " + '{:4.2f}'.format(self.stream.get_cpu_load())
                    + " input latency: " + str(int(self.stream.get_input_latency() * 1000)) + " ms"
                    + " output latency: " + str(int(self.stream.get_output_latency() * 1000)) + " ms",
                    Color.mainwin)

            dots = "b " * self.clicks
            screen.setline_noblock(2, dots, Color.blue)
            self.clicks = (self.clicks + 1) % 40
            tempostring = "cur bpm: " + '{:6.2f}'.format(self.tempo.get_bpm()) +  " confidence: " + '{:4.2f}'.format(self.tempo.get_confidence()) + " " * 20
            screen.setline_noblock(3, tempostring, Color.mainwin)

        audiobuf = samples.tobytes()

        if read < self.hop_s:
            return (audiobuf, pyaudio.paComplete)
        return (audiobuf, pyaudio.paContinue)



class MulticastSender(object):
    def __init__(self):
        pass


class CursesThread(threading.Thread):
    '''
    Der CursesThread ist nur darum hier, damit immer auf Eingaben reagieren
    werden kann
    '''
    def __init__(self, curseslock):
        threading.Thread.__init__(self)
        self.curseslock = curseslock

    def run(self):
        global screen, mode, mode_ctime, mode_prev, server

        while True:
            c = screen.stdscr.getch()

            if c == ord('b'):
                brightness = screen.show_editbox('set max_brightness (0-255)')
                set_max_brightness(brightness)
                screen.refresh()
            if c == ord('s'):
                duration = screen.show_editbox('set strobo_duration (0-30)')
                set_strobo_duration(duration)
                screen.refresh()
            elif c == ord('1'):
                screen.setmode("DEFAULT", Color.green)
                mode = "DEFAULT"
                screen.refresh()
            elif c == ord('2'):
                screen.setmode("BEAT SINGLE", Color.green)
                mode = "BEAT SINGLE"
            elif c == ord('3'):
                screen.setmode("BEAT ALL", Color.green)
                mode = "BEAT ALL"
            elif c == ord('4'):
                if mode == "STROBO":
                    pass
                else:
                    screen.setmode("STROBO", Color.green + curses.A_BLINK)
                    mode_ctime = datetime.now()
                    mode_prev = mode
                    mode = "STROBO"
                    server.send_to_all(b'strobo 0')
            elif c == ord('l'):
                server.list_clients()
            elif c == ord('p'):
                kill_index = screen.show_editbox('kill main() on client')
                kill_client_main(kill_index)
            elif c == ord('r'):
                screen.refresh()

MODEWIN_LINES = 4
MAINWIN_LINES = 10
HELPWIN_LINES = 1

class Screen():
    '''
    Der Screen ist zur einfacheren Handhabung der Curses-Oberfläche.
    '''
    def __init__(self, stdscr, curseslock):
        curses.curs_set(False)

        self.stdscr = stdscr
        self.curseslock = curseslock

        self.stdscr.clear()

        self.y, self.x = self.stdscr.getmaxyx()

        self.modewin = curses.newwin(MODEWIN_LINES, self.x, 0, 0)
        self.modewin.bkgd(Color.mainwin)

        self.mainwin = curses.newwin(MAINWIN_LINES, self.x, MODEWIN_LINES, 0)

        self.mainwin.bkgd(Color.mainwin)

        self.logwin = curses.newwin(self.y - MODEWIN_LINES - MAINWIN_LINES - HELPWIN_LINES, self.x, MODEWIN_LINES + MAINWIN_LINES , 0)
        self.logwin.bkgd(Color.logwin)
        self.logbuffer = []

        self.mainbuffer = []
        for i in range(MAINWIN_LINES):
            self.mainbuffer.append(None)

        self.modebuffer = []
        for i in range(MODEWIN_LINES):
            self.modebuffer.append(None)
        self.modebuffer[2] = ("1 - DEFAULT, 2 - BEAT SINGLE, 3 - BEAT ALL - 4 STROBO", Color.mainwin)

        self.helpwin = curses.newwin(HELPWIN_LINES, self.x, self.y - HELPWIN_LINES, 0)
        self.helpwin.bkgd(Color.helpwin)

        self.refresh()

    def setline_noblock(self, line, msg, format):
        has_lock = self.curseslock.acquire(blocking=False)
        if has_lock:
            self._setline(line, msg, format)
            self.curseslock.release()

    def setline(self, line, msg, format):
        with self.curseslock:
            self._setline(line, msg, format)

    def _setline(self, line, msg, format):
        try:
            #  self.mainwin.addstr(line, 1, " " * (self.x - 2), format)
            #  self.mainwin.addstr(line, 1, msg, format)
            # if this is called during resizing of the terminal, it can fail
            #  self.mainwin.refresh()
            self.mainbuffer[line] = (msg, format)
            self.update_mainwin()
            pass
        except Exception as e:
            print(e)

    def setmode(self, modestring, format):
        self.modebuffer[1] = (" " * (self.x // 2 - len(modestring)) + modestring, format)
        with self.curseslock:
            self.update_modewin()

    def show_editbox(self, title):
        with self.curseslock:
            editwin = curses.newwin(4, 30, screen.y//2, 10)
            editwin.bkgd(curses.color_pair(6))
            editwin.box()
            editwin.addstr(1, 1, title)
            editwin.noutrefresh()
            editwin_inner = curses.newwin(1, 28, screen.y//2+2, 11)
            editwin_inner.noutrefresh()
            curses.doupdate()
            box = Textbox(editwin_inner)
            box.edit()
            return box.gather().strip()


    def resize(self):
        y, x = self.stdscr.getmaxyx()
        if not ( y == self.y and x == self.x):
            self.refresh()

    def refresh(self):
        with self.curseslock:

            curses.endwin()
            self.stdscr.noutrefresh()

            self.y, self.x = self.stdscr.getmaxyx()

            self.mainwin.erase()
            curses.resizeterm(self.y, self.x)

            self.modewin.erase()
            self.modewin.resize(MODEWIN_LINES, self.x)
            self.modewin.box()
            self.modewin.noutrefresh()

            self.mainwin.resize(MAINWIN_LINES, self.x)
            self.mainwin.mvwin(MODEWIN_LINES, 0)
            self.mainwin.box()
            self.mainwin.noutrefresh()

            self.logwin.erase()
            self.logwin.resize(self.y - MODEWIN_LINES - MAINWIN_LINES - HELPWIN_LINES, self.x)

            self.logwin.mvwin(MODEWIN_LINES + MAINWIN_LINES, 0)
            self.logwin.box()
            self.logwin.noutrefresh()

            self.helpwin.erase()
            self.helpwin.resize(HELPWIN_LINES, self.x)
            self.helpwin.mvwin(self.y - HELPWIN_LINES, 0)
            try:
                self.helpwin.addstr(0, 0, 's - set strobo_duration, b - set max_brightness, r - refresh screen, l - list clients, Ctrl-C - quit')
            except Exception:
                pass
            self.helpwin.noutrefresh()

            curses.doupdate()

            self.update_mainwin()
            self.update_modewin()
            self.update_log()

    def update_modewin(self):
        self.modewin.erase()

        count = 0
        for i in self.modebuffer:
            try:
                if i:
                    msg, format = i
                    #  print(msg)
                    self.modewin.addstr(count, 1, msg, format)
            except Exception as e:
                print(e)
            count += 1
        self.modewin.box()
        self.modewin.refresh()

    def update_mainwin(self):
        self.mainwin.erase()

        count = 0
        for i in self.mainbuffer:
            try:
                if i:
                    msg, format = i
                    #  print(msg)
                    self.mainwin.addstr(count, 1, msg, format)
            except Exception as e:
                print(e)
            count += 1
        self.mainwin.box()
        self.mainwin.refresh()

    def update_log(self):
        #  with self.curseslock:
            #  self.logwin.erase()

            count = 1
            for i in self.logbuffer[-20:]:
                try:
                    self.logwin.addstr(count, 1, i)
                except Exception:
                    pass
                count += 1
            #  self.logwin.box()
            self.logwin.refresh()

    def log(self, msg):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.logbuffer.append('%s: %s' %(now, msg))
        #  self.update_log()
        self.refresh()

HOST = "0.0.0.0"
PORT = 7654

class Server(threading.Thread):
    def __init__(self):
        global screen
        threading.Thread.__init__(self)
        # create an INET, STREAMing socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind the socket to a public host, and a well-known port
        self.sock.bind((HOST, PORT))
        # become a server socket
        self.sock.listen(100)
        self.connections = []
        screen.log("Listening on port " + str(PORT))

    def run(self):
        global screen
        while True:
            conn, addr = self.sock.accept()
            self.connections.append((conn, addr));
            #  screen.log("connection from " + str(conn) + " " + str(addr))

            #  from_client = ''
            #  while True:
                #  data = conn.recv(4096)
                #  if not data: break
                #  from_client += data
                #  print from_client
                #  conn.send("I am SERVER\n")
            #  conn.close()
            #  print 'client disconnected'

    def list_clients(self):
        global screen
        count = 0
        for entry in self.connections:
            conn, addr = entry
            screen.log(str(count) + ": " + str(addr))
            count += 1

    def send_to_one(self, index, message):
        global screen
        entry = None
        try:
            entry = self.connections[int(index)]
        except Exception as e:
            screen.log(str(e))
            screen.log("Client does not exist")

        if entry:
            conn, addr = entry
            try:
                conn.send(message + b'\n')
                #  screen.log("sent to " + str(conn) + " " + str(addr))
            except Exception as e:
                screen.log(str(e))
                screen.log("removing " + str(conn) + " " + str(addr))
                conn.close()
                self.connections.remove(entry)

    def send_to_all(self, message):
        global screen
        for entry in list(self.connections):
            conn, addr = entry
            try:
                conn.sendall(message + b'\n')
                #  screen.log("sent to " + str(conn) + " " + str(addr))
            except Exception as e:
                screen.log(str(e))
                screen.log("removing " + str(conn) + " " + str(addr))
                conn.close()
                self.connections.remove(entry)


def main(stdscr):
    global screen, mode, mode_prev, mode_ctime, quallen, server, ping_time

    curseslock = threading.Lock()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    Color.red = curses.color_pair(1)

    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    Color.green = curses.color_pair(2)

    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    Color.blue = curses.color_pair(3)

    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    Color.mainwin = curses.color_pair(4)

    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
    Color.logwin = curses.color_pair(5)

    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    Color.helpwin = curses.color_pair(6)

    screen = Screen(stdscr, curseslock)

    curses_thread = CursesThread(curseslock)
    curses_thread.daemon = True
    curses_thread.start()

    server = Server()
    server.daemon = True
    server.start()

    beat = BeatDetection()
    beat.daemon = True
    beat.start()

    quallen = Quallen()

    # main loop
    while True:
        if mode == "STROBO" and mode_ctime + timedelta(seconds=strobo_duration) < datetime.now():
            screen.setmode(mode_prev, Color.green)
            screen.refresh()
            mode = mode_prev
            mode_prev = "STROBO"
        screen.resize()
        time.sleep(0.01)

        if mode == "DEFAULT" and ping_time + timedelta(seconds=1) < datetime.now():
            server.send_to_all(b'ping')
            ping_time = datetime.now()

def set_max_brightness(_brightness):
    try:
        brightness = int(_brightness)
    except ValueError:
        screen.log('ERROR: brightness must be 0-255')
        return False

    if (brightness < 0 or brightness > 255):
        screen.log('ERROR: brightness must be 0-255')
        return False

    server.send_to_all(b'set max_brightness ' + b'%d' % (brightness))

    screen.log('set max_brightness to %d' %(brightness))
    screen.setline(4, "max_brightness: %d" %(brightness) , Color.green)

def kill_client_main(index):
    server.send_to_one(index, b'kill')
    screen.log('sent kill to client')


def set_strobo_duration(_duration):
    global strobo_duration
    try:
        duration = int(_duration)
    except ValueError:
        screen.log('ERROR: strobo_duration must be 0-30')
        return False

    if (duration < 0 or duration > 30):
        screen.log('ERROR: strobo_duration must be 0-30')
        return False

    strobo_duration = duration
    server.send_to_all(b'set strobo_duration ' + b'%d' % (duration))

    screen.log('set strobo_duration to %d' %(strobo_duration))
    screen.setline(5, "strobo_duration: %d" %(strobo_duration) , Color.green)

if __name__ == '__main__':
    curses.wrapper(main)
