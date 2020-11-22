import requests
import time
import serial
URL =  "http://fluepdot/framebuffer/text?x=0&y=0&font=DejaVuSans12bw_bwfont"
#URL =  "http://fluepdot/framebuffer/text?x=0&y=0&font=fixed_7x14"
spaced_URL = lambda space : "http://fluepdot/framebuffer/text?x={}&y=0&font=DejaVuSans12bw_bwfont".format(space)

def send_string(s):
    with serial.Serial('/dev/ttyUSB0', 115200) as ser:
        text = 'render_font "{}"\r\n'.format(s)
        ser.write(text.encode())

def send_string2(s, space=0):
    try:
        x = requests.post(spaced_URL(space), data=s, timeout=6)

        #print(x.text)
        #if x.status_code == 200:
        #    print("Sucess")
        return 1
    except:
        print("Fail")
        return -1

#sudo chown 666 /dev/ttyUSB0
#sudo docker run -d --name fluepdot --device /dev/ttyUSB0:/fluepdot-device:rwm
#sudo docker exec -it -w "/fluepdot/software/firmware" -e ESPTOOL_PORT='/fluepdot-device' -e ESPTOOL_BAUD='480000' fluepdot make flash

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
            send_string("Wieviele Spieler ?")
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
                    send_string("Wieviel Punkte ?")
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
                        send_string("S{} startet: {}".format(self.cur_player+1,self.points[self.cur_player]))
                        return self.cur_player
            except:
                send_string("Bitte neu versuchen")

    def play(self):
        #send_string("Spieler {} wirft".format(self.cur_player))
        string = "S{} {}".format(self.cur_player+1, self.points[self.cur_player])
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
            send_string("S{} Neu eingeben".format(self.cur_player+1))
            return self.cur_player

        #Substracting thrown points
        if self.points[self.cur_player] - sum(w) >= 0:
            self.points[self.cur_player] -= sum(w)

        next_player = (self.cur_player +1) % self.n_player
        if next_player == 0 and any([p==0 for p in self.points]):
            winners = [i+1 for i,x in enumerate(self.points) if x == 0]
            if len(winners) > 1:
                send_string("Sieger: {}".format(winners))
            else:
                send_string("Spieler {} Siegt".format(winners[0]+1))
            self.state = "Sieger"
            return -1

        spacing = (3 - len(str(self.points[self.cur_player])))*10
        send_string("S{}: {} | S{}: {}".format(self.cur_player+1, self.points[self.cur_player],next_player+1, self.points[next_player]),spacing)

        self.cur_player = next_player
        return self.cur_player

    def get_wurf(self):
        try:
            w = int(eval(input()))
            assert(w >= 0 and w <= 180)

        except:
            #send_string("Eingabe Ungültig")
            w = -1
        return w


def main():
    d = Dart()
    status = d.start()
    while status >= 0:
        status = d.play()

main()