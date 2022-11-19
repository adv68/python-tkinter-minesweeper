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

