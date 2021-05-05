# classifierAgents.py
# parsons/07-oct-2017
#
# Version 1.0
#
# Some simple agents to work with the PacMan AI projects from:
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

# The agents here are extensions written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util
import sys
import os
import csv
import numpy as np
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn import datasets, metrics
from sklearn.metrics import accuracy_score
import math
from scipy.stats import norm
from numpy import mean
from numpy import std

# ClassifierAgent
#
# An agent that runs a classifier to decide what to do.
class ClassifierAgent(Agent):

    # Constructor. This gets run when the agent starts up.
    def __init__(self):
        print "Initialising"

    # Take a string of digits and convert to an array of
    # numbers. Exploits the fact that we know the digits are in the
    # range 0-4.
    #
    # There are undoubtedly more elegant and general ways to do this,
    # exploiting ASCII codes.
    def convertToArray(self, numberString):
        numberArray = []
        for i in range(len(numberString) - 1):
            if numberString[i] == '0':
                numberArray.append(0)
            elif numberString[i] == '1':
                numberArray.append(1)
            elif numberString[i] == '2':
                numberArray.append(2)
            elif numberString[i] == '3':
                numberArray.append(3)
            elif numberString[i] == '4':
                numberArray.append(4)

        return numberArray
                
    # This gets run on startup. Has access to state information.
    #
    # Here we use it to load the training data.
    
    # The below class QuestionAsked is inspired by a Youtube tutorial by Google Developers,
    # https://www.youtube.com/watch?v=LDRbO9a6XPU
    # I have editted the class to better suit the binary decision tree for this project
    class QuestionAsked:

            def __init__(self, column, value):
                self.column = column
                self.value = value
            def is_binary(self,value):
                return value==0 or value==1
            def findMatch(self, data):
                
                if self.is_binary(data[self.column]):
                    return data[self.column] == self.value
                else:
                    print ("not binary!")
    
    #### a class for making evaluation
    class DTNode:
        
        def __init__(self,truePart,falsePart,evaluation):
            
            self.truePart = truePart
            self.falsePart = falsePart
            self.evaluation = evaluation
    #### a class that signify the bottom end of the tree and no further question should be asked     
    class Leaf:
    

        def __init__(self, X,y):
            self.pred = self.typeCountsLeaf(X,y)
        def typeCountsLeaf(self,X,y):
            typecounts = dict()  
            for x in X:
                label = y[X.index(x)]
                if label not in typecounts:
                    typecounts[label] = 0
                typecounts[label] += 1
            return typecounts
    def registerInitialState(self, state):

        # open datafile, extract content into an array, and close.
        self.datafile = open('good-moves.txt', 'r')
        self.datafile2 = open('movesBackForth.txt', 'r')
        self.datafile3 = open('movesEatCapsuleThenChaseGhost.txt', 'r')
        content = self.datafile.readlines()
        content2 = self.datafile2.readlines()
        content3 = self.datafile2.readlines()
        self.datafile.close()
        self.datafile2.close()
        self.datafile3.close()

        #uncomment any below to see results from different training sets or combined
        # note: training on content3 alone caused index out of bound error for some reasons. Required future debugging      

        #content = content2


        #content = content+content2
        #content = content+ content3
        #content = content2+content3

        #content = content + content2 + content3
        self.count = 0

        # Now extract data, which is in the form of strings, into an
        # array of numbers, and separate into matched data and target
        # variables.
        self.data = []
        self.target = []
        # Turn content into nested lists
        for i in range(len(content)):
            lineAsArray = self.convertToArray(content[i])
            dataline = []
            whole = []
            for j in range(len(lineAsArray) - 1):
                dataline.append(lineAsArray[j])
            self.data.append(dataline)
            targetIndex = len(lineAsArray) - 1
            self.target.append(lineAsArray[targetIndex])

        # data and target are both arrays of arbitrary length.
        #
        # data is an array of arrays of integers (0 or 1) indicating state.
        #
        # target is an array of imtegers 0-3 indicating the action
        # taken in that state.
            
        # *********************************************
        #
        # Any other code you want to run on startup goes here.
        #
        # You may wish to create your classifier here.
        #
        # *********************************************
        X = self.data
        y = self.target
        header = ["WallN","WallE","WallS","WallW","FoodN","FoodE","FoodS","FoodW","GNW","GN","GNE","GW","GE","GSW","GS","GSE","GVisible","label"]
        
        #### counting all the labels. returns a dictionary that has the label as keys and its counts as values
        def typeCounts(X,y):
                typecounts = dict()  
                for x in X:
                    label = y[X.index(x)]
                    
                    if label not in typecounts:
                        typecounts[label] = 0
                    typecounts[label] += 1
                return typecounts
        
        ##### a function for calculating entropy
        def cal_entropy(X,y):
            entropy = 0
            for i in typeCounts(X,y).keys():
                p = typeCounts(X,y)[i] / float(len(X)) #divide total number of vectors to get probability
                if p>0: #entropy can't be 0
                    entropy += p * math.log(p, 2) #using math.log, the second parameter is the log base number
            return entropy
            

            
        ##### a function for calculating infromation gain 
        def informationGain(lX,rX,OGProb,X,y):
            subtraction = 0 
            for x in [lX, rX]:
                prob = (len(x) / float(len(X)) )
                subtraction += prob * cal_entropy(lX,y) + prob *cal_entropy(rX,y) # sum of entropy Si multiplies its probability, using formula from the lecture
            iG = OGProb - subtraction
            return iG
        def determine_best_split(X,y):
            highestGain = 0 
            bestQuestionAsked = None 
            for bruh in range(len(X[0])): ###here we only looking at the training parameter, which is the data we initialized excluding the labels (moves)

                values = set([x[bruh] for x in X])  
                for val in values:  

                    question = self.QuestionAsked(bruh, val)

                    true_X, false_X = [], []
                    for x in X:
                        if question.findMatch(x):
                            true_X.append(x)
                        else:
                            false_X.append(x)
                    
                    if len(true_X) == 0 or len(false_X) == 0:
                        continue  #if the true split or the false split of our data is empty then we skip and go to the next spliting
                    
                    infoGain = informationGain(true_X, false_X,cal_entropy(X,y),X,y)
                    
                    if infoGain >= highestGain:
                        highestGain = infoGain
                        bestQuestionAsked = question 
                        #updating the highest gain and best question
            return highestGain, bestQuestionAsked
        def buildDT(X,y,current_depth=0,max_depth=6):
            
            highestGain, bestQuestionAsked = determine_best_split(X,y)
            if current_depth==max_depth:
                print "max depth reached!"
            if highestGain == 0 or current_depth==max_depth:
                return self.Leaf(X,y) #whenever our information gain is 0 or we reached our maximum depth, there's no points asking more questions. Therefore we return a leaf object

            current_depth +=1
            
            true_X, false_X = [], []
            trueLabel, falseLabel = [],[]
            for x in X:
                if bestQuestionAsked.findMatch(x):
                    true_X.append(x)
                    trueLabel.append(y[X.index(x)])
                else:
                    false_X.append(x)
                    falseLabel.append(y[X.index(x)])
            truePart = buildDT(true_X,trueLabel,current_depth,max_depth)

            falsePart = buildDT(false_X,falseLabel,current_depth,max_depth)
            
            return self.DTNode(truePart, falsePart,bestQuestionAsked)

        
        myDT = buildDT(X,y) #build our decision tree
        self.DT = myDT #broaden the scope of our tree so we can use it later for classification

    # Tidy up when Pacman dies
    def final(self, state):

        print "I'm done!"
        self.DT = None #clear the decision tree
        # *********************************************
        #
        # Any code you want to run at the end goes here.
        #
        # *********************************************

    # Turn the numbers from the feature set into actions:
    def convertNumberToMove(self, number):
        if number == 0:
            return Directions.NORTH
        elif number == 1:
            return Directions.EAST
        elif number == 2:
            return Directions.SOUTH
        elif number == 3:
            return Directions.WEST

    # Here we just run the classifier to decide what to do
    def getAction(self, state):
        ### classification function
        def classifyDT(x, DTnode):
            if isinstance(DTnode, self.Leaf):
                return DTnode.pred

        
            if DTnode.evaluation.findMatch(x):
                return classifyDT(x, DTnode.truePart)
            else:
                return classifyDT(x, DTnode.falsePart)
        # How we access the features.
        features = np.array(api.getFeatureVector(state))
        results = classifyDT(features, self.DT)
        pred = max(results, key=results.get) #get the result with the highest probability
        print results
        print pred
        # *****************************************************
        #
        # Here you should insert code to call the classifier to
        # decide what to do based on features and use it to decide
        # what action to take.
        #
        # *******************************************************

        # Get the actions we can try.
        legal = api.legalActions(state)
        
        # getAction has to return a move. Here we pass "STOP" to the
        # API to ask Pacman to stay where they are. We need to pass
        # the set of legal moves to teh API so it can do some safety
        # checking.
        return api.makeMove(self.convertNumberToMove(pred), legal) #use the convertNumberToMove function to translate our intended moves

