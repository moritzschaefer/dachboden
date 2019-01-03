import utime

def startup(sender, player):
    board = player[0] + player[1]

    # set all players fields to zero
    for i in range(len(player[0])):
        player[0][i] = (0,0,0)
        player[1][i] = (0,0,0)
    player[-1][48] = (0,0,0)

    print (player[0])
    #while sum([sum(x) for x in board]) < 100 * 97:

    #starup color
    player[0][24] = (5,0,0);
    for duration in range(200):
        for j in range(len(player[0]//2)):
            sender.send(player[0]+player[1])
            #middle
            if player[0][24] != (100,0,0)
                player[0][24] = (player[0][24]+5,0,0)
            #left
            for i in range(1,j):
                if player[0][24-i] != (100,0,0)
                    player[0][24-i] = (player[0][24-i]+5,0,0)
                    #right
                    if player[0][24+i] != (100,0,0)
                    player[0][24+i] = (player[0][24+i]+5,0,0)
            print (player[0])
            utime.sleep_ms(40)


#
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
