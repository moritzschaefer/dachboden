import utime
import random
PIXELS = 71



def random_Sparkles(sender, spar_board,  n_sparks=30, color="fix", ring=False, strobo_mode = True, sleep_time = 100, max_lights = PIXELS -10):
    spar_board = [(0, 0, 0) for i in range(PIXELS)]
    lights = random.randint(25,max_lights)
    sparks = random.sample(list(range(PIXELS)), lights)
    for i in range(n_sparks):
        if strobo_mode:

            sender.send(spar_board)
            utime.sleep_ms(1)
        if ring:
            if(i==0):
                for s in sparks:
                   spar_board[s] = (random.randint(0, 200), random.randint(0, 200), random.randint(0, 200))
            dark = sparks.pop(0)
            next_light = random.randint(0, PIXELS)
            sparks.append(next_light)
            spar_board[dark] = (0,0,0)
            spar_board[next_light] = (random.randint(0, 200), random.randint(0, 200), random.randint(0, 200))

        else:

            for j in range(PIXELS):
                spar_board[j] = (0,0,0)
            lights = random.randint(25, max_lights)
            sparks = random.sample(list(range(PIXELS)), lights)

            for s in sparks:
                if (color == "fix"):
                    spar_board[s] = (200, 200, 200)
                elif (color == "random"):
                    spar_board[s] = (random.randint(0, 200), random.randint(0, 200), random.randint(0, 200))
        sender.send(spar_board)

        utime.sleep_ms(sleep_time)

def ongoing_lights(sender, stripe):
    stripe = [(0, 0, 0) for i in range(PIXELS)]
    unused = list(range(PIXELS))
    used = []
    for i in range(PIXELS):
        next = random.choice(unused)
        unused.remove(next)
        used.append(next)
        stripe[next] = (200,200,200)
        sender.send(stripe)

def moving_areas(sender, board,  n_moves = 10, area_width=None, n_areas = None, area_color = "white"):


    if(area_width is None):
        area_width = random.randint(15,25)
    if(n_areas is None):
        n_areas = random.randint(PIXELS // (2 * area_width), 2*PIXELS // area_width)
    if(area_color=="white"):
        color = [(200,200,200) for i in range(n_areas)]
    elif(n_areas == 3):
        color = [(200,0,0),(0,200,0),(0,0,200)]
    else:
        color= [(random.randint(0,80),random.randint(0,80),random.randint(0,80)) for i in range(n_areas)]

    viewed_pixels = PIXELS - area_width
    board = [(3, 0, 0) if i < PIXELS // 2 else (0, 0, 3) for i in range(PIXELS)]

    piercer = [bool(random.randint(0,2)) for i in range(n_areas)]
    move_times = [random.randint(100,500) for i in range(n_areas)]
    pos = [random.randint(0,viewed_pixels) for i in range(n_areas)]
    times = [utime.ticks_ms for i in range(n_areas)]
    counts = [0 for i in range(n_areas)]
    directions = [random.choice([-1,1]) for i in range(n_areas)]

    for i in range(n_areas):
        for j in range(area_width):
            r,g,b = board[pos[i]+j]
            r_a, g_a, b_a = color[i]
            board[pos[i] + j] =(min(200,r+r_a),min(200,g+g_a),min(200,b+b_a))
    sender.send(board)
    while(all([x < n_moves for x in counts])):
        changes = False
        for i in range(n_areas):
            if(utime.ticks_diff(utime.ticks_ms(),times[i]) > move_times[i]):
                changes=True
                if(pos[i] >= viewed_pixels and not piercer[i]):
                    directions[i] = -1
                    counts[i] += 1
                    if(random.randint(0,2)):
                        piercer[i] = not piercer[i]
                elif(pos[i] <=0 and not piercer[i]):
                    directions[i] = 1
                    counts[i] += 1
                    if(random.randint(0,2)):
                        piercer[i] = not piercer[i]
                elif( pos[i] + directions[i] != (pos[i] + directions[i]) % PIXELS and piercer[i] ):
                    if (random.randint(0, 2)):
                        piercer[i] = not piercer[i]
                pos[i] = (pos[i] + directions[i]) % PIXELS
                times[i] = utime.ticks_ms()
        if(changes):
            board = [(3, 0, 0) if i < PIXELS // 2 else (0, 0, 3) for i in range(PIXELS)]
            for i in range(n_areas):
                for j in range(area_width):
                    r, g, b = board[(pos[i] + j) % PIXELS]
                    r_a, g_a, b_a = color[i]
                    board[(pos[i] + j) % PIXELS] = (min(200, r + r_a), min(200, g + g_a), min(200, b + b_a))
            sender.send(board)
        else:
            utime.sleep_ms(50)

def strobo(sender,board ,   n_strobes=15):
    strobo_board_dark = [(0, 0, 0) for i in range(PIXELS)]
    strobo_board_bright = [(200, 200, 200) for i in range(PIXELS)]
    for i in range(n_strobes):
        sender.send(strobo_board_dark)
        #utime.sleep_ms(1)
        sender.send(strobo_board_bright)
        #utime.sleep_ms(1)