import time

def getbpm(firsttap, lasttap):
    # prevent div/0
    if(firsttap != lasttap):
        bpm = 60/(firsttap - lasttap)
    else:
        bpm = 0
    return bpm

# get timestamp for first tap
taptime = time.time()

while True:
    now = time.time()
    bpm = getbpm(now, taptime)
    # store current timestamp for next measurement
    taptime = now 
    # wait for next input
    input("Current BPM:" + str(int(bpm)))
    # ANSI escape codes: go up 1 lines, delete line, go to beginning of line
    print("\x1b[1A \x1b[K  \x1b[0G", end="")

