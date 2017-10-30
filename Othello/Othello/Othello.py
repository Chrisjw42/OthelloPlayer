import time
import game as g
import numpy as np

if __name__ == "__main__":
    start = time.time()
    print("Program Begin.")

    gb = g.GameBoard(None)

    g.play_game(gb)
    '''
    for i in np.ndenumerate(gb.state):
        print (i[0])'''
    #print(type(g.gameBoard))


    print("Total time taken: %s sec" % round((time.time() - start), 10))