import utime

def startup(sender, player, color):


    c1 = color[0]
    c2 = color[1]

    # set all players fields to zero
    for i in range(len(player[0])):
        player[0][i] = (0,0,0)
        player[1][i] = (0,0,0)
    player[1][-1] = (0,0,0)

    mid = int(len(player[0]) / 2)

    #full_lights = (sum(c1) + sum(c2)) * 97 / 2
    #player[0][mid] = max(color_per(c1,1),1)
    #player[1][mid] = max(color_per(c2,1),1)

    board = player[0] + player[1]
    n = len(board)
    per_board = [0 for i in range(n)]
    per_board[mid-1] = 1
    per_board[mid + int(len(player[0]))] = 1

    sender.send(board)

    while sum(per_board) < n*100:
        for i in range(n):
            on = 1 if per_board[i] > 0 else 0
            per_board[i] = min(100, per_board[i] + on + int(0.2 * (per_board[max(0, i-1)] + per_board[min(n-1, i+1)])))
        #print(per_board[:48])
        board = [color_per(c1, per_board[i]) if i < len(player[0]) else color_per(c2, per_board[i]) for i in range(n)]
        #print(board[:48])
        utime.sleep_ms(20)
        sender.send(board)

def color_per(c, p):
    new_color = (int(c[0]*p/100), int(c[1]*p/100), int(c[2]*p/100))
    return new_color
