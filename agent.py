import threading
import time
import random

STATE_DEFAULT = 0
STATE_CLICKED = 1
STATE_FLAGGED = 2

class Agent:

    def __init__(self, minesweeper):
        self.ms = minesweeper
        self.thread = threading.Thread(target=self.agentThread)
        self.thread.start()

    def agentThread(self):
        time.sleep(2)     

        p = self.getStateGrid(0,0)
        print("asdf")

        '''
        while self.ms.gameEnded == False:
            for i in range(0, 10):
                for j in range(0, 10):
                    print(self.ms.getState(i, j))
            
            time.sleep(10)
        '''
        '''

        while self.ms.gameEnded == False:
            x = random.randint(0, 9)
            y = random.randint(0, 9)

            while (self.ms.getState(x, y)['state'] != 0):
                x = random.randint(0, 9)
                y = random.randint(0, 9)

            #self.ms.onClick(self.ms.tiles[x][y])
            self.ms.clickTile(x, y)

            time.sleep(0.25)

        print("Done")

        #'''

        #print(self.ms.getState(0, 0))
        #self.ms.onClick(self.ms.tiles[0][0])
        #print(self.ms.getState(0, 0))

    def getStateGrid(self, x, y):
        state = {}
        for i in range(x - 2, x + 3):
            state[i] = {}

            for j in range(y - 2, y + 3):
                state[i][j] = self.ms.getState(i, j)
        return state


    def logicAgent(grid, x, y):
        ownState = grid[x][y]
        if (ownState != -1):
            return (0, 0)

        surroundingCells = getSurrounding(x, y)
        visibleSurroundingCells = []
        for cell in surroundingCells:
            st = grid[cell[0]][cell[1]]
            if st >= 0 and st <= 9:
                visibleSurroundingCells.append(cell)

        


    
    # surVal
    # 1 is bomb
    # 0 safe
    # -1 dont know
    def checkCell(state, x, y):
        ownState = state[x][y]
        if ownState < 0: 
            return (0, 0)

        sur = getSurrounding(x, y)

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
            return (1, 0)

        if ownState <= (surVal.count(1) + surVal.count(-1)):
            return (0, 1)

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

