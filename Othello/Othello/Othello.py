import time
import game as g
import numpy as np
import dbGeneration as dbGen

if __name__ == "__main__":
	print("Program Begin.")
	start = time.time()

	#dbGen.establish_game_database()

	ten, lbl = dbGen.get_tensorinputs_and_labels()

	"""
	gb = g.GameBoard(None)
	g.play_game(gb)
	"""

	print("Total time taken: %s sec" % round((time.time() - start), 10))