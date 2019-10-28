import main
import random
import utime

class Ambiente:

    def __init__(self, sender, n_pixels=97):
        self.sender = sender
        self.n_pixels = n_pixels
        self.pixels = [(0,0,0) for i in range(n_pixels)]
        self.mid = n_pixels // 2
        self.slide_step_time = 50

        self.slide_dir = 0  # 0 Clockwise, 1 Counterclockwise
        self.slide_time = utime.ticks_ms()
        self.counter = 0
        self.moving_slides_init(width = self.mid)
        self.sender.send(self.pixels)
    def ambiente_step(self):

        if random.randint(0,100) < -1:
            self.crazy_swap()
        elif random.randint(0,100) < -2:
            self.swap()
        else:
            if abs(utime.ticks_diff(self.slide_time, utime.ticks_ms())) > self.slide_step_time:
                self.moving_slides_step()
                self.slide_time = utime.ticks_ms()


        self.sender.send(self.pixels)

    def swap(self):
        new_pixels = [self.pixels[i % self.n_pixels] for i in range(self.mid, self.mid+self.n_pixels)]
        self.pixels = new_pixels

    def crazy_swap(self):
        new_pixels = [self.pixels[i] for i in range(self.mid, self.n_pixels)] + [self.pixels[self.mid - i] for i in range(self.mid)]
        self.pixels = new_pixels



    def moving_slides_init(self, width = 4):

        c1, c2 =random.sample([(15,0,0),(0,15,0)],2)
        self.pixels = [c1 if (i//width) % 2 else c2 for i in range(self.n_pixels)]

    def eat_pixel(self):
        last = self.pixels[0]
        for i in range(self.n_pixels):
            if(last == self.pixels[i]):
                continue
            else:
                last = self.pixels[i]
                if(random.randint(0,100) < 10):
                    self.pixels[i] = self.pixels[i-1]
                    return

    def moving_slides_step(self):
        if(random.randint(0,100) < 10):
            self.eat_pixel()
        if self.slide_dir == 0:
            last = self.pixels.pop()
            self.pixels.insert(0, last)
        else:
            first = self.pixels.pop(0)
            self.pixels.append(first)
        self.counter += 1
        if random.randint(0, self.counter+1) > 80 :
            self.counter = 0
            self.slide_dir = (self.slide_dir + 1) % 2
            if random.randint(0, 100) < 10:
                self.moving_slides_init(random.randint(8,self.mid))



