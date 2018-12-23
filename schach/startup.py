import time

def startup(sender, player):
    board = player[0] + player[1]

    # set all players fields to zero
    for i in range(48):
        player[0][i] = (0,0,0)
        player[1][i] = (0,0,0)
    player[1][48] = (0,0,0)

    while sum([sum(x) for x in board]) < 100 * 97:
        pass

#    # fade in/out
#    for i in range(0, 4 * 100):
#        for j in range(n):
#            if (i // 100) % 2 == 0:
#                val = i & 0xff
#            else:
#                val = 255 - (i & 0xff)
#            np[j] = (val, 0, 0)
#        np.write()
#
#    # clear
#    for i in range(n):
#        np[i] = (0, 0, 0)
#    np.write()
