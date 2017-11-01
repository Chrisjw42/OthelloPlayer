import numpy as np
import random
import time
import copy

import collections

# 8 Directions
UP = [-1,0]
UPRIGHT = [-1,1]
RIGHT = [0,1]
DOWNRIGHT = [1,1]
DOWN = [1,0]
DOWNLEFT = [1,-1]
LEFT = [0,-1]
UPLEFT = [-1,-1]

WALLNUMBERS = [0,7]

WALL_BONUS = 5
CORNER_BONUS = 10
EMPTY_CORNER_ADJACENCY_PENALTY = -7


AXES = range(8)



# Storing these manually is much cheaper comutationally that computing manhattan distance for every tile
##                          TOP-LEFT          BOTTOM-RIGHT      TOP-RIGHT         BOTTOM-LEFT          
TILES_ADJACENT_TO_CORNER = [[0,1],[1,0],[1,1],[6,7],[7,6],[6,6],[0,6],[1,7],[1,6],[6,0],[7,1],[6,1]]

DIRECTIONS = [UP, UPRIGHT, RIGHT, DOWNRIGHT, DOWN, DOWNLEFT, LEFT, UPLEFT]

class GameBoard(object):
	"""
	0 = Black team
	1 = White team
	NaN = Empty square

	First index is ROW
	Second index is COLUMN e.g. [2,1] is Third row, second column.

	"""

	__slots__ = ["state", "whosTurn", "parent", "depth"]

	def __init__(self, parent):
		"""
		Initialise gameBoard
		"""
		self.whosTurn = 0
		self.parent = parent
		if not parent == None:
			self.depth = parent.depth
		else:
			self.depth = 0

		self.state = np.empty((8,8))
		for i in self.state:
			for j in range(len(i)):
				i[j] = None

		# Starting positions
		self.state[3][3] = self.state[4][4] = 1
		self.state[3][4] = self.state[4][3] = 0        

		return super().__init__()

	def perform_move(self, moveChoice, whosTurn):

		# Movechoice = [[row, col], dirs]
		square = moveChoice[0]

		# dir = [((row, col), n)], where n is number of steps
		for dir in moveChoice[1]:
			movingSquare = square
			for numSteps in range(dir[1]+1):
				movingSquare = np.add(movingSquare, dir[0])
				self.state[movingSquare[0], movingSquare[1]] = whosTurn
		self.state[square[0], square[1]] = whosTurn

	def __str__(self, **kwargs):
		# include info about who's turn it is, etc. 

		boardPrint = ""
		
		boardPrint += "===== Current Board =====\n".format(self.state)

		for row in range(-1,8):
			if row == -1:
				for col in ["A","B","C","D","E","F","G","H"]:
					boardPrint += "\t{}".format(col)
			else:
				for col in range(8):
					if col == 0:
						boardPrint += "{}".format(row+1)
					if self.state[row][col] == 1 or self.state[row][col] == 0:
						boardPrint += "\t{}".format(int(self.state[row][col]))
					else:
						boardPrint += "\t."
			boardPrint += "\n\n"
		if self.whosTurn == 0:
			boardPrint += "===== Player's turn ====="
		else:
			boardPrint += "===== AI's turn ====="

		return boardPrint


def play_game(board):
	print("Game Begin!")
	playerOutOfMoves = False
	aiOutOfMoves = False

	while(True):
		# Player
		if playerOutOfMoves and aiOutOfMoves == True:
			print("Game Over!")
			who_wins(board)

		print(board)

		if board.whosTurn == 0:
			moves = get_available_moves(board.state, board.whosTurn)

			if len(moves) == 0:
				playerOutOfMoves = True
				board.whosTurn = not board.whosTurn
				continue
			else:
				playerOutOfMoves = False
		
			# choose move, then perform        
			board.perform_move(select_move(moves), board.whosTurn)
		# AI
		else:
			moves = get_available_moves(board.state, board.whosTurn)

			if len(moves) == 0:
				aiOutOfMoves = True
				board.whosTurn = not board.whosTurn
				continue
			else:
				aiOutOfMoves = False
			
			print("Pre move eval:")
			evaluate_state(board.state, board.whosTurn, moves)

			# Choose random move
			suggestedMove = select_move_minimax(board, 2)
			print("Suggested Move: ", suggestedMove)

			#choice = random.randint(0, len(moves)-1)
			#print("Choosing move at random")
			board.perform_move(suggestedMove, board.whosTurn)
			
			print("Post move eval:")
			evaluate_state(board.state, board.whosTurn, moves)
			
		board.whosTurn = not board.whosTurn

def select_move_minimax(board, maxDepth):
	def get_child_boards(board):
		moves = get_available_moves(board.state, board.whosTurn)
		child_boards = []
		thisDepth = board.depth + 1

		# For every possible move
		for move in moves:
			# copy the board, perform the move
			
			b = copy.deepcopy(board)

			b.perform_move(move, board.whosTurn)
			b.depth = thisDepth
			b.whosTurn = not b.whosTurn

			# Don't evaluate boards on generation, many wil not need to be evaluated. 
			child_boards.append(b)

		return child_boards

	# Note, this function utilises the maxDepth of the outer function (select_move_minimax)
	def evaluate_board_ab_pruning(board, alpha, beta):
		#print("Depth: {}, Turn: {}".format(board.depth, board.whosTurn))
		if board.depth == maxDepth:
			print("d: {}, hit max Depth".format(board.depth, board.whosTurn))

			val = evaluate_state(board.state, board.whosTurn, print_messages = False)
			return val 
		else:
			children = get_child_boards(board)
			children_with_values = {}



			# JUST STARTED TO BEGIN a-B pruning implementation

			# Should each call return an a and B value? No, just need the a and B value to check against. Check OneNote red circle in a-B page.


			# Recursively recall this function until hitting the floor (maxDepth)
			for child in children:
				value = evaluate_board_ab_pruning(child, -999, 999)
				# NOTE - THIS CURRENTLY IS OVERWRITING WHEN THERE ARE MULTIPLE CHILDREN WITH THE SAME SCORE
				children_with_values[value] = child

			# This player tries to maximise the score
			if board.whosTurn == whosTurnMinimax:
				#print("d: {}, MAX:  ".format(board.depth), children_with_values)

				# If on the final level, return not only the score, but the board itself.
				if board.depth == 0:
					return max(children_with_values.keys()), children_with_values[max(children_with_values.keys())]
				return max(children_with_values.keys())
			# Simulate enemy player trying to minimise
			else:
				#print("d: {}, MIN: ".format(board.depth), children_with_values)
				return min(children_with_values.keys()), 

	whosTurnMinimax = board.whosTurn
	# Results[0] is the score, results[1] is the board
	results = evaluate_board_ab_pruning(board, -999, 999)
	print("EVAL SCORE:", results[0])

	print(results)

	# Check which of the available moves matches the minimax result (this is a turd way to do this, I am sorry)

	#COULD INSTEAD JUST RETURN A BOARD THAT HAS ALREADY PERFORMED THE MOVE

	moves = get_available_moves(board.state, board.whosTurn)

	print("BEST MOVE: \n", results[1].state)
	maskedTargetState = np.ma.array(results[1].state, mask=np.isnan(results[1].state))
	maskedTargetState = np.ma.filled(maskedTargetState, 2)
	#print("MASKED: \n", maskedTargetState)

	for m in moves:
		b = copy.deepcopy(board)
		b.perform_move(m, board.whosTurn)
		
		#print("checking move: \n", b.state)

		maskedTestState = np.ma.array(b.state, mask=np.isnan(b.state))
		maskedTestState = np.ma.filled(maskedTestState, 2)
		# Mask the two arrays to ignore the Nan values. Allows comparison1
		if np.ma.all(maskedTestState == maskedTargetState):
			return m
	
def evaluate_state(state, whosTurn, availableMoves = None, print_messages = True):
	start = time.time()
	evalScore = 0

	if availableMoves == None:
		availableMoves = get_available_moves(state, whosTurn)
	# Number of potential free moves for each player, each potential move adds +1
	myScore = len(availableMoves)
	enemyScore = len(get_available_moves(state, not whosTurn))
	""" # temporarily disabled to increase clarity of debugging

	myScore = 0
	enemyScore = 0"""

	# IMPROVEMENT - TILES ADJACENT TO EMPTY WALL SLOT SHOULD BE PENALISED

	# NOTE - Time to begin implementing minimax, yo

	for row in AXES:
		for col in AXES:
			thisPieceTeam = state[row][col]
			if np.isnan(thisPieceTeam):
				continue

			scoreWeight = 1

			# Adjacent to corner
			if [row,col] in TILES_ADJACENT_TO_CORNER:
				# Which corner?
				if row < 4:
					if col < 4: #Upper-left
						relevantCorner = [0,0]
					else: #Upper-right
						relevantCorner = [0,7]
				else: 
					if col < 4: # Lower-left
						relevantCorner = [7,0]
					else: # Lower-Right
						relevantCorner = [7,7]
				if np.isnan(state[relevantCorner[0]][relevantCorner[1]]):
					# The relevant corner is empty, you're gonna have a bad time. 
					if print_messages:
						if thisPieceTeam == 1:
							print("\t\t", end='')
						print("{} Is adjacent to an empty corner (-7)".format([row+1,col+1]))
					scoreWeight = EMPTY_CORNER_ADJACENCY_PENALTY
				else:
					if print_messages:
						if thisPieceTeam == 1:
							print("\t\t", end='')
						print("{} Is adjacent to a filled corner empty corner (+5)".format([row+1,col+1]))
					scoreWeight = WALL_BONUS

			# Next to at least 1 wall
			elif row in WALLNUMBERS or col in WALLNUMBERS:
				# Corner
				if row in WALLNUMBERS and col in WALLNUMBERS:
					scoreWeight = CORNER_BONUS
					if print_messages:
						if thisPieceTeam == 1:
							print("\t\t", end='')
						print("{} Is in a corner (+10)".format([row+1,col+1]))

				# Adjacent to a wall
				else:
					scoreWeight = WALL_BONUS
					if print_messages:
						if thisPieceTeam == 1:
							print("\t\t", end='')
						print("{} Is adjacent to a wall (+5)".format([row+1,col+1]))
					
			if thisPieceTeam == whosTurn:
				evalScore += 1*scoreWeight
				myScore += 1*scoreWeight
			else:
				evalScore -= 1*scoreWeight
				enemyScore += 1*scoreWeight
	if print_messages:
		print("\tmyScore: {}".format(myScore))
		print("\tenemyScore: {}".format(enemyScore))

		print("Took {} sec".format(round(time.time() - start, 4)))

	return myScore

### Functions declared outside of classs to keep gameBoard lightweight
def who_wins(board):
	num0 = 0
	num1 = 0

	for i in board.state:
		for j in i:
			if j == 0:
				num0 = num0 + 1
			elif j == 1:
				num1 = num1 + 1

	print("Player 0: {}".format(num0))
	print("Player 1: {}".format(num1))

	if num0 > num1:
		print("Player 0 wins!")
	elif num1 > num0:
		print("Player 1 wins!")
	else:
		print("We have a draw!")
	input()
	exit()

def get_square_moves(row, col, state, whosTurn):
	curSquare = np.array([row,col])
	content = state[curSquare[0],curSquare[1]]

	squareMoves = []

#    [(),(),()]

	# square is taken
	if not np.isnan(content):
		return None

	for dir in DIRECTIONS:
		# The moving square will move one step in a given direction at a time
		movingSquare = np.array([row,col])

		# Move 1 step in the given direction
		movingSquare = np.add(movingSquare, dir)

		try:
			# We find out what is in the first square in this direction
			movingContent = state[movingSquare[0],movingSquare[1]]

			if np.isnan(movingContent): # empty square
				continue
			elif movingContent == whosTurn: # piece in adjacent square matches this player's colour
				continue
			else: # Enemy piece in square
				steps = 0
				# Continue stepping in this direction to find out if this direction yields a valid move
				while True:
					steps = steps + 1
					movingSquare = np.add(movingSquare, dir)

					# If moved out of range
					if movingSquare[0] not in AXES or movingSquare[1] not in AXES:
						break

					# This may step out of range, in which case the loop will continue
					movingContent = state[movingSquare[0], movingSquare[1]]

					if np.isnan(movingContent): # empty square
						# Not fruitful, there was an enemy, but no friend to capture with
						break
					elif not movingContent == whosTurn: # Another friend
						continue
					elif movingContent == whosTurn:# Found friend to capture with
						squareMoves.append((dir, steps))
						break

		except(IndexError):
			continue

	if len(squareMoves) == 0:
		return None
	return squareMoves

def get_available_moves(state, whosTurn):
	availableMoves = []
	for row in range(8):
		for col in range(8):

			thisSquareMoves = get_square_moves(row, col, state, whosTurn)
			if not thisSquareMoves == None:
				availableMoves.append([[row, col], thisSquareMoves])

	return availableMoves

def select_move(availableMoves):
	moveNumbers = range(len(availableMoves))

	for i in moveNumbers:
		print("{}:\trow:{} col:{}".format((i+1), availableMoves[i][0][0]+1,availableMoves[i][0][1]+1))
	
	choice = ""
	while not choice in moveNumbers:
		print("Select your move! Please input a number from 1 - {}!...".format(len(availableMoves)))
		try:
			choice = int(input()) - 1
		except:
			print("Please input an integer!")

	print("You have selected {}: {}".format(choice + 1, availableMoves[choice][0]))
	return availableMoves[choice]

def get_artificial_boards(listMoves):
	"""
	Artificially replay through a game, returning a board for every state in the game
	
	Returns: matrix of each turn of the game
	"""
	gb = GameBoard(None)
	whosTurn = 0
	states = []
	
	for mv in listMoves:

		mv = mv.lower()
		# Convert "A8" input to [7,0] == [row, col]
		mv = [int(mv[1]) - 1, ord(mv[0]) - 97]

		moves = get_available_moves(gb.state, whosTurn)
		
		if len(moves) == 0:
			gb.whosTurn = not gb.whosTurn
		else:
			for move in moves:
				if move[0] == mv:
					gb.perform_move(move, whosTurn)
					states.append(copy.deepcopy(gb.state))
					whosTurn = not whosTurn
					done = True
					break
			'''if done == False:
				print(len(moves))
				#print("PRBLEM - THIS INDICATES THAT THE PLAYER HAD NO MOVES TO MAKE, MUST IMPLEMENT 'SKIP MOVE' ")
				print("PRBLEM")'''
		
	return states



		
def convert_board_to_tensorinput(board):
	tensorinput = board.state

	for y in range(8):
		for x in range(8):

			# Black
			if tensorinput[x, y] == 0:
				tensorinput[x, y] = -1
			# Not white (empty)
			elif not tensorinput[x, y] == 1:
				tensorinput[x, y] = 0
	print(tensorinput)


"""
# Note, this function utilises the maxDepth of the outer function (select_move_minimax)
	def evaluate_board(board):
		#print("Depth: {}, Turn: {}".format(board.depth, board.whosTurn))
		if board.depth == maxDepth:
			print("d: {}, hit max Depth".format(board.depth, board.whosTurn))

			val = evaluate_state(board.state, board.whosTurn, print_messages = False)
			return val 
		else:
			children = get_child_boards(board)
			children_with_values = {}

			# Recursively recall this function until hitting the floor (maxDepth)
			for child in children:
				# NOTE - THIS CURRENTLY IS OVERWRITING WHEN THERE ARE MULTIPLE CHILDREN WITH THE SAME SCORE
				children_with_values[evaluate_board(child)] = child

			# This player tries to maximise the score
			if board.whosTurn == whosTurnMinimax:
				print("d: {}, MAX:  ".format(board.depth), children_with_values)

				# If on the final level, return not only the score, but the board itself.
				if board.depth == 0:
					return max(children_with_values.keys()), children_with_values[max(children_with_values.keys())]
				return max(children_with_values.keys())
			# Simulate enemy player trying to minimise
			else:
				print("d: {}, MIN: ".format(board.depth), children_with_values)
				return min(children_with_values.keys()), 
"""