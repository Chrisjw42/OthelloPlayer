import numpy as np
from bs4 import BeautifulSoup
import requests
import json
import os
import game 
import pickle


def _create_game_urls():
	gameURLs = []
	for round in range(1,13):
		for t in range(1, 25): # extra numbers, some not actually associated with games
			url = "http://www.o-wc.com/live/t{}/{}.html".format(round, t)
			gameURLs.append(url)
	return gameURLs

# Web scraper for pulling down the game info
def _get_games():
	games = {}
	gameURLs = _create_game_urls()
	sess = requests.Session()

	for gameURL in gameURLs:
		print(gameURL)

		r = sess.get(gameURL)

		if r.status_code == 200:
			# Grab the html element for the game table
			try:

				soup = BeautifulSoup(r.text)
				gameTable = soup.find_all("table", id="gameTable")

				# Convert the text to a string and get all the rows from it.
				scoreBlack = soup.find_all("label", id="scoreBlack")[0].text
				scoreWhite = soup.find_all("label", id="scoreWhite")[0].text
				listMoves = soup.find_all(attrs={"name": "ListMoves"})[0]["value"].strip()

				games[gameURL] = {"ScoreBlack": scoreBlack,
						 "ScoreWhite": scoreWhite,
						 "ListMoves": listMoves}
				print(games[gameURL])
				#print(r.text)
			except:
				pass
		else:
			print("{} Failed".format(gameURL))
	return games

def _establish_game_database(override = False):
	if not os.path.isfile("data/gamedb.json") or override:
		with open("data/gamedb.json", "w") as fp:

			fp.write(json.dumps(_get_games(), indent=4))

	# Process Data
	with open("data/gamedb.json", "r") as fp:
		games = json.load(fp)

	for g in games:
		games[g]["ListMoves"] = str(games[g]["ListMoves"]).upper()
		if games[g]["ScoreWhite"] > games[g]["ScoreBlack"]:
			games[g]["Winner"] = "White"
		else:
			games[g]["Winner"] = "Black"

		moves = games[g]["ListMoves"]
		movesArr = []
		for idx in range(int(len(moves) / 2)):
			movesArr.append(moves[idx*2:idx*2+2])

		games[g]["ListMoves"] = movesArr
	
	with open("data/gamedb.json", "w") as fp:
		fp.write(json.dumps(games, indent=4))

def convert_state_to_tensorformat(state):
	state = state.reshape(64)
	state[state == 0] = -1
	state[np.isnan(state)] = 0

	return state

def get_tensorinputs_and_labels(forceNew = False):
	if not os.path.isfile("data/gamedb.json"):
		print("There is no Game DB")
		_establish_game_database()

	# If the processing has not ben performed, or forcing new
	if not os.path.isfile("data/tensorinputs.p") or not os.path.isfile("data/labels.p") or forceNew:
		labels = []
		tensorinputs = []
		db = {}
		# open db

		with open("data/gamedb.json") as fp:
			db = json.load(fp)

		for i in list(db.keys()):
			print(i)
			thisGame = db[i]
			boardStates = game.get_artificial_boards(thisGame["ListMoves"])

			for i in boardStates:
				tensorinputs.append(convert_state_to_tensorformat(i))
				if thisGame["Winner"] == "Black":
					labels.append(-1)
				else:
					labels.append(1)

			# Only do it once
			#break
		pickle.dump(tensorinputs, open("data/tensorinputs.p", "wb"))
		pickle.dump(labels, open("data/labels.p", "wb"))
	else:
		tensorinputs = pickle.load(open("data/tensorinputs.p", "rb"))
		labels = pickle.load(open("data/labels.p", "rb"))

	print("Returned {} data points".format(len(tensorinputs)))
	return tensorinputs, labels
		