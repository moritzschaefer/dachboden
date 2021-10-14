import requests
import time
import serial

spaced_URL = lambda space: f"http://fluepdot/framebuffer/text?x={space}&y=0&font=DejaVuSans12bw_bwfont"

def send_string_serial(string):
    with serial.Serial("/dev/ttyUSB0", 115200) as ser:
        text = f'render_font "{string}"\r\n'
        ser.write(text.encode())
    return string


class Dart:
    def __init__(self):
        self.player_count = 2
        self.state = "START"
        self.start_points = 301
        self.current_player = 0
        self.current_throw = 0
        self.points = []

    def start(self):
        while True:
            send_string_serial("Wie viele Spieler?")
            try:
                player_count = int(input())
                if player_count > 5:
                    send_string_serial("Max. 5 Spieler")
                    time.sleep(4)
                    continue
                elif player_count < 1:
                    send_string_serial("Min. 1 Spieler")
                    time.sleep(4)
                    continue
                else:
                    send_string_serial("Wie viele Punkte?")
                    start_points = int(input())
                    if start_points < 1:
                        send_string_serial("Min. 1 Punkt")
                        time.sleep(4)
                        continue
                    else:
                        self.player_count = player_count
                        self.start_points = start_points
                        self.points = [
                            self.start_points for i in range(self.player_count)
                        ]
                        self.current_player = 0
                        self.current_throw = 0
                        self.state = "Play"
                        send_string_serial(
                            f"S{self.current_player + 1} startet: {self.points[self.current_player]}"
                        )
                        return self.current_player
            except:
                send_string_serial("Bitte neu versuchen")

    def play(self):
        string = f"S{self.current_player + 1} {self.points[self.current_player]}"

        throw_points = [0, 0, 0]
        i = 0

        # Waiting to input 3 throws
        while i < 3:
            throw_points[i] = self.get_wurf()

            if throw_points[i] >= 0:
                string = string + f"-{throw_points[i]}"
                send_string_serial(string)
                i += 1

        try:
            confirm = input()
        except:
            confirm = "-"

        if "-" in confirm:
            send_string_serial(f"S{self.current_player + 1} neu eingeben")
            return self.current_player

        # Substract thrown points
        if self.points[self.current_player] - sum(throw_points) >= 0:
            self.points[self.current_player] -= sum(throw_points)

        next_player = (self.current_player + 1) % self.player_count

        # Check whether the game is over
        if next_player == 0 and any([p == 0 for p in self.points]):
            winners = [i for i, x in enumerate(self.points) if x == 0]
            if len(winners) > 1:
                send_string_serial(f"Sieger: {list(map(lambda i: i + 1, winners))}")
            else:
                send_string_serial(f"Spieler {winners[0] + 1} siegt")
            self.state = "Sieger"
            return -1

        send_string_serial(
            f"S{self.current_player + 1}: {self.points[self.current_player]} | S{next_player + 1}: {self.points[next_player]}"
        )

        self.current_player = next_player
        return self.current_player

    def get_wurf(self):
        try:
            throw_point = int(eval(input()))
            assert throw_point >= 0 and throw_point <= 180
        except:
            throw_point = -1
        return throw_point


def main():
    d = Dart()
    status = d.start()
    while status >= 0:
        status = d.play()


main()
