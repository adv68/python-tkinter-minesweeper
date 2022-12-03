import threading
import time
import random
import csv
from tensorflow import keras
import numpy as np
import pandas as pd

import requests

# Number of games to simulate
# CHANGE THIS FLAG TO SET THE NUMBER OF GAMES TO RUN IN A ROW
NUM_GAMES = 25


# The agent class starts a thread and calls the configured agent to play the game of minesweeper
class Agent:

    def __init__(self, minesweeper):
        # initial setup configuration
        self.ms = minesweeper
        self.stop = False
        self.gameCounter = 0
        self.adjustedGameCounter = 0
        self.winCounter = 0
        self.gameEnded = False

        self.ms.setStopHandler(self.gameEndHandler)

        self.csvFile = "output.csv"

        # START AGENT CONFIG FLAGS
        
        # Set to true to output moves to "output.csv"
        self.outputCsv = False

        # Used to configure action agent to use to make decisions
        # Un comment the agent you want to use
        #self.actionAgent = LogicAgentActionChooser()
        #self.actionAgent = KerasANNAgentActionChooser()
        self.actionAgent = MLNETAgentActionChooser()

        # END AGENT CONFIG FLAGS

        self.actionAgent.setup()

        # start up the agent thread
        self.thread = threading.Thread(target=self.agentThread)
        self.thread.start()

    # called by the minesweeper game to signal the thread to cleanup and exit
    def stopThread(self):
        self.stop = True

    # the end of game handler that is applied to the minesweeper game
    def gameEndHandler(self, won):
        # increment game counter and adjustedgamecounter
        self.gameCounter = self.gameCounter + 1
        if self.startRand == False:
            self.adjustedGameCounter = self.adjustedGameCounter + 1

        # track and output game win/loss status
        if won:
            self.winCounter = self.winCounter + 1
            print("Won  ", self.gameCounter)
        else:
            print("Lost ", self.gameCounter)

        # signal agent thread to prepare for new game
        self.gameEnded = True

        # return whether or not to quit
        return self.gameCounter >= NUM_GAMES

    # agent thread loop
    def agentThread(self):
        # wait for gui to initialize if need be
        time.sleep(1)     

        # open csv file for output (just in case we need it)
        with open(self.csvFile, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)

            # loop until gui tells us to quit
            while self.stop == False:
                cellActions = {}
                randMove = False

                self.startRand = True

                # loop until this game is done
                while self.gameEnded == False:
                    # if there are no pending actions in our list, search for some
                    # the nested for loops will scan the entire board, and pass the 5x5 grid for each cell into 
                    # the selected agent for processing. If the agent says take an action on this cell, the action
                    # is added to the pending actions list
                    if len(cellActions) == 0:
                        for i in range(0, 10):
                            for j in range(0, 10):
                                grid = self.getStateGrid(i, j)
                                act = self.actionAgent.getActions(grid, i, j)
                                if act.count(1) > 0:
                                    cellActions[(i, j)] = act

                                # csv writer for for model builder data
                                actSingle = 0
                                if act[0] == 1:
                                    actSingle = 1
                                elif act[1] == 1: 
                                    actSingle = 2
                                if self.outputCsv:
                                    if act.count(1) > 0 or random.random() > 0.99:
                                        row = []
                                        for k in range(i - 2, i + 3):
                                            row = row + list(grid[k].values())
                                        #row = row + list(act) # use this line for keras output data
                                        row.append(actSingle) # use this line for ML.NET output data
                                        csvwriter.writerow(row) 
                                # end csv writer

                        # if we still haven't discovered any actions, then do a random move
                        if len(cellActions) == 0:
                            randMove = True

                        # added for screenshot purposes only
                        # comment out or not
                        else:
                            print("waiting")
                            time.sleep(10)


                    # search for a random tile to click until we find and unclicked cell, then click it
                    if randMove:
                        randX = random.randint(0, 9)
                        randY = random.randint(0, 9)

                        while (self.ms.getState(randX, randY) != -1):
                            randX = random.randint(0, 9)
                            randY = random.randint(0, 9)

                        self.ms.clickTile(randX, randY)

                        randMove = False
                    # if not in random move mode, take the first action from pending actions and run it
                    else:
                        self.startRand = False
                        for c, a in cellActions.items():
                            if (a[0] == 1):
                                self.ms.clickTile(c[0], c[1])
                            elif (a[1] == 1):
                                self.ms.flagTile(c[0], c[1])

                            cellActions.pop(c)
                            break
                    
                    # comment out if your are running simulations
                    # use if you want to watch the game play
                    #time.sleep(0.1)
                
                # once game is done, delay and reset flag
                time.sleep(0.5)
                self.gameEnded = False

        # print game statistics
        print("Played", self.gameCounter, "games")
        print("Played (adjusted)", self.adjustedGameCounter, "games")
        print("Won", self.winCounter, "games")
        print(self.winCounter / self.gameCounter, "Success rate")
        print(self.winCounter / self.adjustedGameCounter, "Adjusted success rate")

    # returns the 5x5 state grid
    def getStateGrid(self, x, y):
        state = {}
        for i in range(x - 2, x + 3):
            state[i] = {}

            for j in range(y - 2, y + 3):
                state[i][j] = self.ms.getState(i, j)
        return state

    # gets the 8 surrounding cell indices
    def getSurrounding(x, y):
        return [
            (x,     y + 1),
            (x + 1, y + 1),
            (x + 1, y    ),
            (x + 1, y - 1),
            (x,     y - 1),
            (x - 1, y - 1),
            (x - 1, y    ),
            (x - 1, y + 1)
        ]

# parent class for all action agents
class AgentActionChooser:
    # setup runs initialization logic
    def setup(self):
        pass

    # get actions returns actions to take, if any
    def getActions(self, grid, x, y):
        return (0, 0)

# Logic Agent implementation of AgentActionChooser
class LogicAgentActionChooser(AgentActionChooser):
    # gets an action by scanning the surrounding cells
    # if any have their bomb counts satisfied, we are safe, so click
    # if any have the same number of hidden/flagged cells surrounding as number of bombs, we
    # know we are a bomb so flag
    # If we dont know anything, return (0, 0) for do nothing 
    def getActions(self, grid, x, y):
        ownState = grid[x][y]
        if (ownState != -1):
            return (0, 0)

        surroundingCells = Agent.getSurrounding(x, y)
        visibleSurroundingCells = []
        for cell in surroundingCells:
            st = grid[cell[0]][cell[1]]
            if st >= 0 and st <= 9:
                visibleSurroundingCells.append(cell)

        vals = []
        for cell in visibleSurroundingCells:
            vals.append(self.checkCell(grid, cell[0], cell[1]))

        if vals.count(1) > 0:
            return (0, 1)
        elif vals.count(0) > 0:
            return (1, 0)
        
        return (0, 0)

    # helper function for agent
    # surVal
    # 1 is bomb
    # 0 safe
    # -1 dont know
    def checkCell(self, state, x, y):
        ownState = state[x][y]
        if ownState < 0: 
            return -1

        sur = Agent.getSurrounding(x, y)

        surVal = []
        for cell in sur:
            val = state[cell[0]][cell[1]]
            if (val == 10):
                surVal.append(1)
                continue
            elif (val >= 0 and val <= 9):
                surVal.append(0)
            else:
                surVal.append(-1)

        if ownState == surVal.count(1):
            return 0

        if ownState >= (surVal.count(1) + surVal.count(-1)):
            return 1

        return -1

# Keras ANN Agent implementation of AgentActionChooser
class KerasANNAgentActionChooser(AgentActionChooser):
    # loads the model in setup
    def setup(self):
        super().setup()

        self.model = keras.models.load_model("keras_model5")

    # gets the actions from the model by passing the input into the model and returning the model prediction
    # there is a comparison for just in case model doesnt return a perfect 1 or 0
    def getActions(self, grid, x, y):
        row = []
        for i in range(x - 2, x + 3):
            row = row + list(grid[i].values())

        rowArray = np.asarray([np.asarray(row)])
        rowdf = pd.DataFrame(rowArray)

        val = self.model.predict(
            rowdf.iloc[:, 0 : 25].values,
            batch_size=1    
        )

        tup = (val[0][0], val[0][1])
        tupAdjusted = (
            0 if tup[0] < 0.6 else 1,
            0 if tup[1] < 0.6 else 1
        )

        print(row)
        print(tup)
        print(tupAdjusted)

        return tupAdjusted

# ML.NET Agent implementation of AgentActionChooser
class MLNETAgentActionChooser(AgentActionChooser):
    # define url for web api - note that port may need to change based on your system
    def setup(self):
        super().setup()

        self.url = "https://localhost:49723/predict"

    # get an action from the ML.NET api server
    # first, it builds a dictionary of inputs
    # then it sends the input to the server as json via post and converts the response value 
    # into the action tuple, which it returns
    def getActions(self, grid, x, y):
        row = []
        for i in range(x - 2, x + 3):
            row = row + list(grid[i].values())

        rowArray = np.asarray([np.asarray(row)])

        data = {
            "in_u2l2": row[0],
            "in_u2l1": row[1],
            "in_u2": row[2],
            "in_u2r1": row[3],
            "in_u2r2": row[4],
            "in_u1l2": row[5],
            "in_u1l1": row[6],
            "in_u1": row[7],
            "in_u1r1": row[8],
            "in_u1r2": row[9],
            "in_l2": row[10],
            "in_l1": row[11],
            "in_0": row[12],
            "in_r1": row[13],
            "in_r2": row[14],
            "in_d1l2": row[15],
            "in_d1l1": row[16],
            "in_d1": row[17],
            "in_d1r1": row[18],
            "in_d1r2": row[19],
            "in_d2l2": row[20],
            "in_d2l1": row[21],
            "in_d2": row[22],
            "in_d2r1": row[23],
            "in_d2r2": row[24]
        }

        res = requests.post(self.url, json = data, verify=False)
        resJson = res.json()
        val = resJson["prediction"]

        tup = (1 if val == 1 else 0, 1 if val == 2 else 0)
        tupAdjusted = (
            0 if tup[0] < 0.6 else 1,
            0 if tup[1] < 0.6 else 1
        )

        print(row)
        print(tup)
        print(tupAdjusted)

        return tupAdjusted

