# Python Version 2.7.3
# File: minesweeper.py

# The minesweeper game was developed by ripexz (github.com/ripexz)
# All additions for CIS 365 project are surrounded by comments and are commented
# The rest remains as it was at the fork

from tkinter import *
from tkinter import messagebox as tkMessageBox
from collections import deque
import random
import platform
import time as timesleep
from datetime import time, date, datetime

from agent import Agent

SIZE_X = 10
SIZE_Y = 10

STATE_DEFAULT = 0
STATE_CLICKED = 1
STATE_FLAGGED = 2

BTN_CLICK = "<Button-1>"
BTN_FLAG = "<Button-2>" if platform.system() == 'Darwin' else "<Button-3>"

window = None

class Minesweeper:

    def __init__(self, tk):

        # import images
        self.images = {
            "plain": PhotoImage(file = "images/tile_plain.gif"),
            "clicked": PhotoImage(file = "images/tile_clicked.gif"),
            "mine": PhotoImage(file = "images/tile_mine.gif"),
            "flag": PhotoImage(file = "images/tile_flag.gif"),
            "wrong": PhotoImage(file = "images/tile_wrong.gif"),
            "numbers": []
        }
        for i in range(1, 9):
            self.images["numbers"].append(PhotoImage(file = "images/tile_"+str(i)+".gif"))

        # set up frame
        self.tk = tk
        self.frame = Frame(self.tk)
        self.frame.pack()

        # set up labels/UI
        self.labels = {
            "time": Label(self.frame, text = "00:00:00"),
            "mines": Label(self.frame, text = "Mines: 0"),
            "flags": Label(self.frame, text = "Flags: 0")
        }
        self.labels["time"].grid(row = 0, column = 0, columnspan = SIZE_Y) # top full width
        self.labels["mines"].grid(row = SIZE_X+1, column = 0, columnspan = int(SIZE_Y/2)) # bottom left
        self.labels["flags"].grid(row = SIZE_X+1, column = int(SIZE_Y/2)-1, columnspan = int(SIZE_Y/2)) # bottom right

        self.restart() # start game
        self.updateTimer() # init timer


    def setup(self):
        # create flag and clicked tile variables
        self.flagCount = 0
        self.correctFlagCount = 0
        self.clickedCount = 0
        self.startTime = None


        # ADDED SECTION
        # set up bools for tracking game state
        self.gameEnded = False
        self.won = False
        # END ADDED SECTION


        # create buttons
        self.tiles = dict({})
        self.mines = 0
        for x in range(0, SIZE_X):
            for y in range(0, SIZE_Y):
                if y == 0:
                    self.tiles[x] = {}

                id = str(x) + "_" + str(y)
                isMine = False

                # tile image changeable for debug reasons:
                gfx = self.images["plain"]

                # currently random amount of mines
                if random.uniform(0.0, 1.0) < 0.1:
                    isMine = True
                    self.mines += 1

                tile = {
                    "id": id,
                    "isMine": isMine,
                    "state": STATE_DEFAULT,
                    "coords": {
                        "x": x,
                        "y": y
                    },
                    "button": Button(self.frame, image = gfx),
                    "mines": 0 # calculated after grid is built
                }

                tile["button"].bind(BTN_CLICK, self.onClickWrapper(x, y))
                tile["button"].bind(BTN_FLAG, self.onRightClickWrapper(x, y))
                tile["button"].grid( row = x+1, column = y ) # offset by 1 row for timer

                self.tiles[x][y] = tile

        # loop again to find nearby mines and display number on tile
        for x in range(0, SIZE_X):
            for y in range(0, SIZE_Y):
                mc = 0
                for n in self.getNeighbors(x, y):
                    mc += 1 if n["isMine"] else 0
                self.tiles[x][y]["mines"] = mc

    def restart(self):
        self.setup()
        self.refreshLabels()

    def refreshLabels(self):
        self.labels["flags"].config(text = "Flags: "+str(self.flagCount))
        self.labels["mines"].config(text = "Mines: "+str(self.mines))

    def gameOver(self, won):
        for x in range(0, SIZE_X):
            for y in range(0, SIZE_Y):
                if self.tiles[x][y]["isMine"] == False and self.tiles[x][y]["state"] == STATE_FLAGGED:
                    self.tiles[x][y]["button"].config(image = self.images["wrong"])
                if self.tiles[x][y]["isMine"] == True and self.tiles[x][y]["state"] != STATE_FLAGGED:
                    self.tiles[x][y]["button"].config(image = self.images["mine"])

        self.tk.update()


        # ADDED SECTION
        # set game end flags
        self.gameEnded = True
        self.won = won

        # if no stop handler is registered, run the original end of game handler
        if self.stopHandler == None:
            # ORIGINAL END OF GAME CODE
            msg = "You Win! Play again?" if won else "You Lose! Play again?"
            res = tkMessageBox.askyesno("Game Over", msg)
            if res:
                self.restart()
            else:
                self.tk.quit()
            # END ORIGINAL END CODE
        else:
            # run the stop handler which returns a bool. if true quit, otherwise restart
            if self.stopHandler(won):
                self.tk.quit()
            else:
                self.restart()
        # END ADDED SECTION


        #msg = "You Win! Play again?" if won else "You Lose! Play again?"
        #res = tkMessageBox.askyesno("Game Over", msg)
        #if res:
        #    self.restart()
        #else:
        #    self.tk.quit()

    def updateTimer(self):
        ts = "00:00:00"
        if self.startTime != None:
            delta = datetime.now() - self.startTime
            ts = str(delta).split('.')[0] # drop ms
            if delta.total_seconds() < 36000:
                ts = "0" + ts # zero-pad
        self.labels["time"].config(text = ts)
        self.frame.after(100, self.updateTimer)

    def getNeighbors(self, x, y):
        neighbors = []
        coords = [
            {"x": x-1,  "y": y-1},  #top right
            {"x": x-1,  "y": y},    #top middle
            {"x": x-1,  "y": y+1},  #top left
            {"x": x,    "y": y-1},  #left
            {"x": x,    "y": y+1},  #right
            {"x": x+1,  "y": y-1},  #bottom right
            {"x": x+1,  "y": y},    #bottom middle
            {"x": x+1,  "y": y+1},  #bottom left
        ]
        for n in coords:
            try:
                neighbors.append(self.tiles[n["x"]][n["y"]])
            except KeyError:
                pass
        return neighbors

    def onClickWrapper(self, x, y):
        return lambda Button: self.onClick(self.tiles[x][y])

    def onRightClickWrapper(self, x, y):
        return lambda Button: self.onRightClick(self.tiles[x][y])

    def onClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()

        if tile["isMine"] == True:
            # end game
            self.gameOver(False)
            return

        # change image
        if tile["mines"] == 0:
            tile["button"].config(image = self.images["clicked"])
            self.clearSurroundingTiles(tile["id"])
        else:
            tile["button"].config(image = self.images["numbers"][tile["mines"]-1])
        # if not already set as clicked, change state and count
        if tile["state"] != STATE_CLICKED:
            tile["state"] = STATE_CLICKED
            self.clickedCount += 1
        if self.clickedCount == (SIZE_X * SIZE_Y) - self.mines:
            self.gameOver(True)

    def onRightClick(self, tile):
        if self.startTime == None:
            self.startTime = datetime.now()

        # if not clicked
        if tile["state"] == STATE_DEFAULT:
            tile["button"].config(image = self.images["flag"])
            tile["state"] = STATE_FLAGGED
            tile["button"].unbind(BTN_CLICK)
            # if a mine
            if tile["isMine"] == True:
                self.correctFlagCount += 1
            self.flagCount += 1
            self.refreshLabels()
        # if flagged, unflag
        elif tile["state"] == 2:
            tile["button"].config(image = self.images["plain"])
            tile["state"] = 0
            tile["button"].bind(BTN_CLICK, self.onClickWrapper(tile["coords"]["x"], tile["coords"]["y"]))
            # if a mine
            if tile["isMine"] == True:
                self.correctFlagCount -= 1
            self.flagCount -= 1
            self.refreshLabels()

    def clearSurroundingTiles(self, id):
        queue = deque([id])

        while len(queue) != 0:
            key = queue.popleft()
            parts = key.split("_")
            x = int(parts[0])
            y = int(parts[1])

            for tile in self.getNeighbors(x, y):
                self.clearTile(tile, queue)

    def clearTile(self, tile, queue):
        if tile["state"] != STATE_DEFAULT:
            return

        if tile["mines"] == 0:
            tile["button"].config(image = self.images["clicked"])
            queue.append(tile["id"])
        else:
            tile["button"].config(image = self.images["numbers"][tile["mines"]-1])

        tile["state"] = STATE_CLICKED
        self.clickedCount += 1

    # SECTION ADDED FOR AGENT

    # return the current state of a given tile
    # -2 doesnt exist
    # -1 dont know
    # 0 clear
    # 1-9 visible number
    # 10 flagged as bomb
    def getState(self, x, y):
        try:
            tile = self.tiles[x][y]
            if tile["state"] == STATE_FLAGGED:
                return 10
            elif tile["state"] == STATE_CLICKED:
                return tile["mines"]
            else:
                return -1
        except KeyError:
            return -2

    # simulate a click on a tile (left click)
    def clickTile(self, x, y):
        t = self.tiles[x][y]
        t["button"].configure(bg = "#444444")
        self.onClick(t)

    # simulate a tile flag (right click)
    def flagTile(self, x, y):
        t = self.tiles[x][y]
        t["button"].configure(bg = "#444444")
        self.onRightClick(t)

    # register a stop handler for the game
    def setStopHandler(self, handler):
        self.stopHandler = handler
    # END SECTION ADDED FOR AGENT

### END OF CLASSES ###

def main():
    # create Tk instance
    window = Tk()
    # set program title
    window.title("Minesweeper")
    # create game instance
    minesweeper = Minesweeper(window)

    # setup agent instance
    agent = Agent(minesweeper)

    # run event loop
    window.mainloop()

    # stop agent thread before exit
    agent.stopThread()

if __name__ == "__main__":
    main()
