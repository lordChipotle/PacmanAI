# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

# Reused from Practical 5
# This is a class that creates a grid-like map. Beneficial for later use of mapping for the game
class Grid:
         
    # Constructor
    #
    # Note that it creates variables:
    #
    # grid:   an array that has one position for each element in the grid.
    # width:  the width of the grid
    # height: the height of the grid
    #
    # Grid elements are not restricted, so you can place whatever you
    # like at each location. You just have to be careful how you
    # handle the elements when you use them.
    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row=[]
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid


    # Print the grid out.
    def display(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print

    # The display function prints the grid out upside down. This
    # prints the grid out so that it matches the view we see when we
    # look at Pacman.
    def prettyDisplay(self):       
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[self.height - (i + 1)][j],
            # A new line after each line of the grid
            print 
        # A line after the grid
        print
        
    # Set and get the values of specific elements in the grid.
    # Here x and y are indices.
    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    # Return width and height to support functions that manipulate the
    # values stored in the grid.
    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

class MDPAgent(Agent):

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"

        print api.whereAmI(state)
        self.makeMap(state)
        self.addWallsToMap(state)
        self.addConsumablesToMap(state)

        self.map.display()
    # This is what gets run in between multiple games
    def final(self, state):
        print "Looks like the game just ended!"

    # Returns the layout height of the map
    def getLayoutHeight(self, corners):
        height = -1
        for i in range(len(corners)):
            if corners[i][1] > height:
                height = corners[i][1]
        return height + 1
    
    # Returns the layout width of the map
    def getLayoutWidth(self, corners):
        width = -1
        for i in range(len(corners)):
            if corners[i][0] > width:
                width = corners[i][0]
        return width + 1
    #creates the map
    def makeMap(self,state):
        corners = api.corners(state)
        height = self.getLayoutHeight(corners)
        width  = self.getLayoutWidth(corners)
        self.map = Grid(width, height) #map is used for storing the original values of the items in the map
        self.dankMap = Grid(width, height) #while dankMap is used for value iteration later on

    #query all the walls location from the api and add it to corresponding location in th map
    def addWallsToMap(self, state):
        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], '%')
        self.dankMap = self.map

    #Create a map with a current picture of the food that exists.
    def addConsumablesToMap(self, state):
        # First, make all grid elements that aren't walls blank.
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != '%':
                    self.map.setValue(i, j, 0)
        food = api.food(state)
        for i in range(len(food)):
            self.map.setValue(food[i][0], food[i][1], 5)
        bigPillEnergy = api.capsules(state)
        for i in range(len(bigPillEnergy)):
            self.map.setValue(bigPillEnergy[i][0],bigPillEnergy[i][1],15)
        self.dankMap = self.map
    
    #due to the fact that ghosts will have changing position and states, we update them every turn
    def updateGhosts(self,state):
        ghosts = api.ghosts(state)
        ghostStatesWithTimes= api.ghostStatesWithTimes(state)

        for g in ghostStatesWithTimes:
            ghostVal = 1.2*g[1]-20
            self.map.setValue(int(g[0][0]),int(g[0][1]),ghostVal) 
            #g[0] here is the coordinates of the respective ghost 
            # and g[1] is how much time till ghosts revert from edible state to hunting pacman
            # with 0 being not edible anymore

        self.dankMap =self.map #update map to dankMap
  
    #a dictionary for identifying legal moves before value iteration
    def legalPos(self,x,y):
        
        n = (x,y+1)
        s = (x,y-1)
        w = (x-1,y)
        e = (x+1,y)
        legalDict = {}
        if self.map.getValue(n[0],n[1]) != '%':
            legalDict["N"] = n
        if self.map.getValue(s[0],s[1]) != '%':
            legalDict["S"] = s
        if self.map.getValue(w[0],w[1]) != '%':
            legalDict["W"] = w
        if self.map.getValue(e[0],e[1]) != '%':
            legalDict["E"] = e
        return legalDict
    
    #a dictionary that is similar to the previous but for post-value-iteration
    def legalPosD(self,x,y):
        
        n = (x,y+1)
        s = (x,y-1)
        w = (x-1,y)
        e = (x+1,y)
        legalDict = {}
        if self.dankMap.getValue(n[0],n[1]) != '%':
            legalDict["N"] = n
        if self.dankMap.getValue(s[0],s[1]) != '%':
            legalDict["S"] = s
        if self.dankMap.getValue(w[0],w[1]) != '%':
            legalDict["W"] = w
        if self.dankMap.getValue(e[0],e[1]) != '%':
            legalDict["E"] = e
        return legalDict
    
    #a similar dictionary to the previous but for direction referencing
    def legalDirD(self,x,y):
        n = (x,y+1)
        s = (x,y-1)
        w = (x-1,y)
        e = (x+1,y)
        dirDict = {}
        if self.dankMap.getValue(n[0],n[1]) != '%':
            dirDict["N"] = Directions.NORTH
        if self.dankMap.getValue(s[0],s[1]) != '%':
            dirDict["S"] = Directions.SOUTH
        if self.dankMap.getValue(w[0],w[1]) != '%':
            dirDict["W"] = Directions.WEST
        if self.dankMap.getValue(e[0],e[1]) != '%':
            dirDict["E"] = Directions.EAST
        return dirDict
    
    # outputs the side direction of current direction for utility calculation
    def sideSqueeze(self,x,y,dir):
        self.x = x
        self.y = y
        dirLabel = ""
        dirDict = {"N":Directions.NORTH,"S":Directions.SOUTH,"W":Directions.WEST,"E":Directions.EAST}
        for dirKey,dirVal in dirDict.items():
            if dirVal == dir:
                dirLabel = dirKey
        if dirLabel == "N" or dirLabel == "S":
            w = (x-1,y)
            e = (x+1,y)
            return [w,e]
        elif dirLabel == "W" or dirLabel == "E":
            n = (x,y+1)
            s = (x,y-1)
            return [n,s]
        else:
            print "Something went wrong, go debug here"
    
    #Calculates all the expected utilities of a specific spot. return as a list
    def calcExpectedU(self,x,y):
        
    
        legalDict = self.legalPos(x,y) #using the legalPos dictionary to identify if a direction is aiming towards a wall
        if "N" in legalDict:
            nu = self.map.getValue(x,y+1)
        else:
            nu = self.map.getValue(x,y)
        if "S" in legalDict:
            su = self.map.getValue(x,y-1)
        else:
            su = self.map.getValue(x,y)
        if "E" in legalDict:
            eu = self.map.getValue(x+1,y)
        else:
            eu = self.map.getValue(x,y)
        if "W" in legalDict:
            wu = self.map.getValue(x-1,y)
        else:
            wu = self.map.getValue(x,y)
        

        moveup = 0.8* nu+0.1*wu+0.1*eu
        movedown = 0.8* su+0.1*wu+0.1*eu
        moveleft = 0.8* wu+0.1*nu+0.1*su
        moveright = 0.8* eu+0.1*nu+0.1*su
        return [moveup,movedown,moveleft,moveright]

    #Calculate the minimum expected utility from the previous utilities list
    def MinU (self,x,y):
        return min(self.calcExpectedU(x,y))
    
    #Same as MinU() except for calculating the maximum
    def MaxU (self,x,y):
        return max(self.calcExpectedU(x,y))

    # Value Iteration for small grid setup
    def valIterS (self,state,discount,reward):
        pacman = api.whereAmI(state)
        walls= api.walls(state)
        food = api.food(state)
        ghosts = api.ghosts(state)
        bigPillEnergy = api.capsules(state)
        corners = api.corners(state)
        for i in range(self.getLayoutWidth(corners) - 1):
            for j in range (self.getLayoutHeight(corners) - 1):
                if (i,j) not in walls and (i,j)not in ghosts and (i,j) not in bigPillEnergy and (i,j) not in food:
                    if len(food)<=1:
                        u = self.MaxU(i,j)
                        #when the food is less 1 or 0 (could be pointless when it's 0 but just making sure), 
                        # we want the pacman to eat the last food as soon as possible
                    else:

                        u = self.MinU(i,j)
                        # However, when the food is more than 1. Since it's a small grid, avoiding the ghost(s) is priority
                    bellman = reward + discount* u 
                    self.dankMap.setValue(i,j,bellman) 
                    #for every value iteration, we only update the dankMap.That's where we going to calculate our next move policy from

    # a function works as a radar for ghost(with the radar centers being on the ghosts themselves)
    # it is a useful function for later on determining conditions where pacman is within a range of certain distance (7 in my design) from ghosts
    # the method is inspired from a method mentioned in a data science blog called "Ramblings about Data"
    # Reference:leyankoh.com/2017/12/14/an-mdp-solver-for-pacman-to-navigate-a-nondeterministic-environment/. , 23 Jan. 2018, 
    
    def ghostsRadar(self,state):
        ghosts = api.ghosts(state)
        radar = []
        for g in range(len(ghosts)):
            
            for i in range (7):
            
                n = (int(ghosts[g][0]),int(ghosts[g][1])+i) #North
                nw = (int(ghosts[g][0]-i),int(ghosts[g][1])+i) #North West
                ne = (int(ghosts[g][0]+i),int(ghosts[g][1])+i) #North East

                s = (int(ghosts[g][0]),int(ghosts[g][1])-i) #South 
                sw = (int(ghosts[g][0]-i),int(ghosts[g][1])-i) #South West
                se = (int(ghosts[g][0]+i),int(ghosts[g][1])-i) #South East

                e = (int(ghosts[g][0])+i,int(ghosts[g][1])) #East
                w = (int(ghosts[g][0])-i,int(ghosts[g][1])) #West

                if n not in radar:
                    radar.append(n)
                if s not in radar:
                    radar.append(s)

                if nw not in radar:
                    radar.append(nw)
                if sw not in radar:
                    radar.append(sw)
                if ne not in radar:
                    radar.append(ne)
                if se not in radar:
                    radar.append(se)
            
                if w not in radar:
                    radar.append(w)
                if e not in radar:
                    radar.append(e)
            
        return radar              
    
    #Value iteration function for the mediumClassic grid setup
    def valIterM(self,state,discount,reward):
        pacman = api.whereAmI(state)
        walls= api.walls(state)
        food = api.food(state)
        ghosts = api.ghosts(state)
        bigPillEnergy = api.capsules(state)
        corners = api.corners(state)
        foodOutOfRadar = [] #initializing a list that will store all the food that's outside of the radar
        radar = self.ghostsRadar(state)
        for f in food:
            if f not in radar:
                foodOutOfRadar.append(f)
                #Here we trying to find out what food should not be influnenced by the ghosts' negative values
        for i in range(self.getLayoutWidth(corners) - 1):
            for j in range (self.getLayoutHeight(corners) - 1):
                
                if (i,j) not in walls and (i,j)not in ghosts and (i,j) not in bigPillEnergy and (i,j) not in foodOutOfRadar: 
                    #by letting the food around ghosts negatively propageted, we make sure the pacman receives a headup when he's close to ghosts
                

                    u = self.MaxU(i,j) 
                    
                    bellman = reward + discount* u 
                    self.dankMap.setValue(i,j,bellman)
                    #for every value iteration, we only update the dankMap.That's where we going to calculate our next move policy from


    #a function that calculate the best policy for the next move
    def plannedMove(self,x,y):
        destination = (0,0)
        utilsDict = {}
        legalDict = self.legalPosD(x,y)
        dirDict = self.legalDirD(x,y)

        #we iterate through the legal moves dictionary function we made earlier and calculates the respective expected utility for each legal direction
        for lKey,lVal in legalDict.items():
            pos = lVal
            dir = dirDict[lKey]
            util = 0.0
            if self.dankMap.getValue(pos[0],pos[1])!= "%":
                util += 0.8*self.dankMap.getValue(pos[0],pos[1])
            else:
                util += 0
            sideSqueezeList = self.sideSqueeze(x,y,dir)
            for sideMove in sideSqueezeList:
                if self.dankMap.getValue(sideMove[0],sideMove[1])!= "%":
                    util+= 0.1*self.dankMap.getValue(sideMove[0],sideMove[1])
                else:
                    util += 0
            utilsDict[dir] = util
        
        #we find the maximum of all legal expected utilities
        maxUtility = max(utilsDict.values())

        #then we find its corresponding direction
        for direction,utility in utilsDict.items():
            if utility == maxUtility:
                destination = direction
        
        return destination

    #the function that determine your move every turn. We just gonna throw all the stuffs we made in there.
    def getAction(self, state):
        self.makeMap(state)
        self.addWallsToMap(state)
        self.addConsumablesToMap(state)
        self.updateGhosts(state)
        # Get the actions we can try, and remove "STOP" if that is one of them.
        pacman = api.whereAmI(state)
        legal = api.legalActions(state)
        ghosts = api.ghosts(state)
        corners = api.corners(state)
        layoutHeight = self.getLayoutHeight(corners)
        layoutWidth = self.getLayoutWidth(corners)
        
        if (layoutHeight-1)<8 and (layoutWidth-1)<8:
            for i in range (100):
                self.valIterS(state,0.68,-0.1)
        else:
            for i in range (50):
                self.valIterM(state,0.8,-0.1)
        plannedMove = self.plannedMove(pacman[0],pacman[1])
        #self.dankMap.prettyDisplay()
        #Feel free to uncomment this if you like to see the values generated

        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        
        #Input the calculated move for our next move
        return api.makeMove(plannedMove, legal)
