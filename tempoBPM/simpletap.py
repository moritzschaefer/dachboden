import time

def promptBPM():
    #print("\x1b[1A \x1b[2K", end="")
    bpm = input("Press Enter to \"tap\".")
    if(bpm):
        bpm = int(bpm)
    return bpm
def checkBPM(bpm, userbpm):
    if(bpm != userbpm):
        #print("\x1b[1A \x1b[0J", end="")
        checkBPM(bpm,promptBPM())
    else:
        return print("task validated")
    #tap = time.time()
    #if self.totalTaps <= 0:
    #    # if this is the first tap
    #    self.firstTap = tap
    #    self.lastTap = tap
    #else:
    #    self.bpm = 60.0 / (tap - self.lastTap)
    #    self.bpmAvg = 60.0 / ((tap - self.firstTap) / self.totalTaps)
    #
    #self.totalTaps += 1
    #self.lastTap = tap

targetBPM = 6
currentBPM = 0

while True:
    checkBPM(targetBPM, promptBPM())
#    time.sleep(1)
    # prompt for bpm
    # calculate bpm
    # delete last line
    # print new lie with new bpm
    # wait for 0.5 seconds
