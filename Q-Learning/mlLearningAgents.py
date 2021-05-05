# mlLearningAgents.py
# parsons/27-mar-2017
#
# A stub for a reinforcement learning agent to work with the Pacman
# piece of the Berkeley AI project:
#
# http://ai.berkeley.edu/reinforcement.html
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

# The agent here was written by Simon Parsons, based on the code in
# pacmanAgents.py
# learningAgents.py

from pacman import Directions
from game import Agent
import random
import game
import util


# QLearnAgent
#
class QLearnAgent(Agent):

    # Constructor, called when we start running the
    def __init__(self, alpha=0.2, epsilon=0.05, gamma=0.8, numTraining=10):
        # alpha       - learning rate
        # epsilon     - exploration rate
        # gamma       - discount factor
        # numTraining - number of training episodes
        #
        # These values are either passed from the command line or are
        # set to the default values above. We need to create and set
        # variables for them
        self.alpha = float(alpha)
        self.epsilon = float(epsilon)
        self.gamma = float(gamma)
        self.numTraining = int(numTraining)
        # Count the number of games we have played
        self.episodesSoFar = 0
        # The use of util.Counter() is mentioned on the website of Berkeley Pacman AI Project:
        # "Utilities, including util.Counter, which is particularly useful for Q-learners."
        # Link:http://ai.berkeley.edu/reinforcement.html
        self.qval = util.Counter()
        self.prevState = None
        self.prevAction = None
        self.currentScore = 0

    # Accessor functions for the variable episodesSoFars controlling learning
    def incrementEpisodesSoFar(self):
        self.episodesSoFar += 1

    def getEpisodesSoFar(self):
        return self.episodesSoFar

    def getNumTraining(self):
        return self.numTraining

    # Accessor functions for parameters
    def setEpsilon(self, value):
        self.epsilon = value

    def getAlpha(self):
        return self.alpha

    def setAlpha(self, value):
        self.alpha = value

    def getGamma(self):
        return self.gamma

    def getMaxAttempts(self):
        return self.maxAttempts
    # Querying a Q value
    def getQval(self, state, action):
        return self.qval[(state, action)]
    # Find the maximum Q value
    def findMaxQval(self, state):
        legal = state.getLegalPacmanActions()

        Qs = [self.getQval(state, act) for act in legal]
        if len(Qs) == 0:
            return 0
        else:
            return max(Qs)
    # update the Q value as the weighted sum of old value and the learned value
    # Inspired by examples from https://deeplizard.com/learn/video/HGeI30uATws
    def updateQval(self, prevState, prevAction, state, reward, maxQ):
        legal = state.getLegalPacmanActions()
        if len(legal) == 0:
            reward = reward
        else:
            reward = reward + (self.gamma * maxQ)

        self.qval[(prevState, prevAction)] = (1 - self.alpha) * self.getQval(prevState,
                                                                             prevAction) + self.alpha * reward
    # Find the action associated with the highest Q value
    def findOptimalAction(self, state):
        legal = state.getLegalPacmanActions()
        bestAction = None

        cur = 0
        for act in legal:
            Q = self.getQval(state, act)
            if (Q > cur) or (bestAction is None):
                cur = Q
                bestAction = act
        return bestAction

    # Make decision on whether to explore or eploit the Q values we had at current step
    # Also known as greedy episilon
    def exploreorexploit(self,e,legal,optimal):
        randomNum = random.random()
        if randomNum<e:
            return random.choice(legal)
        else:
            return optimal
    # getAction
    #
    # The main method required by the game. Called every time that
    # Pacman is expected to move
    def getAction(self, state):

        # The data we have about the state of the game
        legal = state.getLegalPacmanActions()
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        maxQ = self.findMaxQval(state)

        # In case if we are at the initial state
        if self.prevState is not None:
            self.updateQval(self.prevState, self.prevAction, state, (state.getScore() - self.currentScore), maxQ)
        # make a decision, either explore the area or move based on the Q values we got
        optimalAction = self.exploreorexploit(self.epsilon,legal,self.findOptimalAction(state))
        pick = optimalAction

        #For debugging use
        print
        "Legal moves: ", legal
        print
        "Score: ", state.getScore()
        print
        "Current score", self.currentScore
        print
        "Move:", pick
        # Update the key variables for referencing and calculation in the next move
        self.currentScore = state.getScore()
        self.prevState = state
        self.prevAction = pick
        return pick

    # Handle the end of episodes
    #
    # This is called by the game after a win or a loss.
    def final(self, state):

        print
        "A game just ended!"
        # Gradually decrease the episilon value to increase exploitation as we get more and more of the whole Q value table
        self.setEpsilon(self.epsilon - self.epsilon * 0.25)
        # Calculate and update final reward and Q value
        final = state.getScore() - self.currentScore

        self.updateQval(self.prevState, self.prevAction, state, final, 0)
        # Reset the referencing variables for next run
        self.currentScore = 0
        self.prevState = None
        self.prevAction = None


        # Keep track of the number of games played, and set learning
        # parameters to zero when we are done with the pre-set number
        # of training episodes
        self.incrementEpisodesSoFar()
        if self.getEpisodesSoFar() == self.getNumTraining():
            msg = 'Training Done (turning off epsilon and alpha)'
            print
            '%s\n%s' % (msg, '-' * len(msg))
            self.setAlpha(0)
            self.setEpsilon(0)


