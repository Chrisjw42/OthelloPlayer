import time
import game as g
import numpy as np
import dbGeneration as dbGen
#import convert

import tensorflow as tf

if __name__ == "__main__":
	print("Program Begin.")
	start = time.time()

	#dbGen.establish_game_database()

	#ten, lbl = dbGen.get_tensorinputs_and_labels(forceNew = True)

	gb = g.GameBoard(None)
	g.play_game(gb, maxSearchDepth = 3)
	

	#dbGen.try_read()

	#dbGen.get_tensorinputs_and_labels(True)

	#dbGen.get_tensorinputs_and_labels()

	#dbGen._convert_movelists_to_json(dbGen._convert_wtb_to_move_lists())

	print("Total time taken: %s sec" % round((time.time() - start), 10))
