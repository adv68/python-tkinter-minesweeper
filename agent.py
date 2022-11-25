import threading
import time
import random
import csv
from tensorflow import keras
import numpy as np
import pandas as pd



# Number of games to simulate
NUM_GAMES = 5

class Agent:

    def __init__(self, minesweeper):
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
        #self.actionAgent = LogicAgentActionChooser()
        self.actionAgent = KerasANNAgentActionChooser()
        self.actionAgent.setup()

        # END AGENT CONFIG FLAGS

        self.thread = threading.Thread(target=self.agentThread)
        self.thread.start()

    def stopThread(self):
        self.stop = True

    def gameEndHandler(self, won):
        self.gameCounter = self.gameCounter + 1
        if self.startRand == False:
            self.adjustedGameCounter = self.adjustedGameCounter + 1
        if won:
            self.winCounter = self.winCounter + 1
            print("Won  ", self.gameCounter)
        else:
            print("Lost ", self.gameCounter)
        self.gameEnded = True
        return self.gameCounter >= NUM_GAMES

    def agentThread(self):
        time.sleep(1)     

        with open(self.csvFile, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)

            while self.stop == False:
                cellActions = {}
                randMove = False

                self.startRand = True

                while self.gameEnded == False:
                    if len(cellActions) == 0:
                        for i in range(0, 10):
                            for j in range(0, 10):
                                grid = self.getStateGrid(i, j)
                                #act = self.logicAgentGetActions(grid, i, j)
                                act = self.actionAgent.getActions(grid, i, j)
                                if act.count(1) > 0:
                                    cellActions[(i, j)] = act

                                # csv writer for for model builder data
                                if self.outputCsv:
                                    if act.count(1) > 0 or random.random() > 0.99:
                                        row = []
                                        for k in range(i - 2, i + 3):
                                            row = row + list(grid[k].values())
                                        row = row + list(act)
                                        csvwriter.writerow(row) 
                                # end csv writer

                        if len(cellActions) == 0:
                            randMove = True

                    if randMove:
                        randX = random.randint(0, 9)
                        randY = random.randint(0, 9)

                        while (self.ms.getState(randX, randY) != -1):
                            randX = random.randint(0, 9)
                            randY = random.randint(0, 9)

                        self.ms.clickTile(randX, randY)

                        randMove = False
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
                
                time.sleep(0.5)
                self.gameEnded = False

        print("Played", self.gameCounter, "games")
        print("Played (adjusted)", self.adjustedGameCounter, "games")
        print("Won", self.winCounter, "games")
        print(self.winCounter / self.gameCounter, "Success rate")
        print(self.winCounter / self.adjustedGameCounter, "Adjusted success rate")

    def getStateGrid(self, x, y):
        state = {}
        for i in range(x - 2, x + 3):
            state[i] = {}

            for j in range(y - 2, y + 3):
                state[i][j] = self.ms.getState(i, j)
        return state


    # returns tuple (val1, val2)
    # val1 is whether or not to click
    # val2 is whether or not to flag
    def logicAgentGetActions(self, grid, x, y):
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


class AgentActionChooser:
    def setup(self):
        pass

    def getActions(self, grid, x, y):
        return (0, 0)

class LogicAgentActionChooser(AgentActionChooser):
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

class KerasANNAgentActionChooser(AgentActionChooser):
    def setup(self):
        super().setup()

        #self.model = keras.models.load_model("keras_model")
        self.model = keras.models.load_model("keras_model5")

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
        #return super().getActions(grid, x, y)