import requests
import time
URL =  'https://www.w3schools.com/python/demopage.php'

def send_string(s):
    print("Gesendet {}".format(s))
    return
    myobj = {"value": s}
    x = requests.post(URL, data = myobj)
    print(x.text)
    if x.status_code == 200:
        print("Sucess")

class Dart:
    def __init__(self):
        self.n_player = 2
        self.state = "START"
        self.start_point = 301
        self.cur_player = 0
        self.cur_throw = 0
        self.points = []

    def start(self):

        while True:
            send_string("Wieviele Spieler?")
            try:
                n_player = int(input())
                if n_player > 5:
                    send_string("Max 5 Spieler")
                    time.sleep(4)
                    continue
                elif n_player < 1:
                    send_string("Min 1 Spieler")
                    time.sleep(4)
                    continue
                else:
                    send_string("Wieviel Punkte?")
                    start_points = int(input())
                    if start_points <1:
                        send_string("Min 1 Punkt")
                        time.sleep(4)
                        continue
                    else:
                        self.n_player = n_player
                        self.start_point = start_points
                        self.points = [self.start_point for i in range(self.n_player)]
                        self.cur_player = 0
                        self.cur_throw = 0
                        self.state = "Play"
                        send_string("S{} Starts".format(self.cur_player))
                        return self.cur_player
            except:
                send_string("Bitte neu versuchen")

    def play(self):
        #send_string("Spieler {} wirft".format(self.cur_player))
        string = "S{} {}".format(self.cur_player, self.points[self.cur_player])
        #send_string(string)
        w = [0,0,0]
        i = 0
        #Waiting to input 3 Throws
        while i < 3:
            w[i] = self.get_wurf()
            if w[i] >= 0:
                string = string + "-{}".format(w[i])
                send_string(string)
                i +=1

        try:
            confirm = input()
        except:
            confirm = "-"

        if "-" in confirm:
            send_string("S{} Neu eingeben".format(self.cur_player))
            return self.cur_player

        #Substracting thrown points
        if self.points[self.cur_player] - sum(w) >= 0:
            self.points[self.cur_player] -= sum(w)

        next_player = (self.cur_player +1) % self.n_player
        if next_player == 0 and any([p==0 for p in self.points]):
            winners = [i for i,x in enumerate(self.points) if x == 0]
            if len(winners) > 1:
                send_string("Spieler {} Siegen".format(winners))
            else:
                send_string("Spieler {} Siegt".format(winners[0]))
            self.state = "Sieger"
            return -1

        send_string("S{}: {} Next S{}: {}".format(self.cur_player, self.points[self.cur_player],next_player, self.points[next_player]))

        self.cur_player = next_player
        return self.cur_player

    def get_wurf(self):
        try:
            w = int(eval(input()))
            assert(w >= 0 and w <= 180)

        except:
            send_string("Eingabe Ungültig")
            w = -1
        return w


def main():
    d = Dart()
    status = d.start()
    while status >= 0:
        status = d.play()

main()