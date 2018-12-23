import utime

def stroboscope(sender, board):
    for j in range(100):
        board = [(15,15,15) for i in range(97)]
        sender.send(board)
        board = [(0,0,0) for i in range(97)]
        sender.send(board)

# versin without sender (10% faster)
def stroboscopeOld(np):
    for j in range(100):
        for i in range(97):
            np[i] = (15,15,15)
        np.write()
        for i in range(97):
            np[i] = (0,0,0)
        np.write()
