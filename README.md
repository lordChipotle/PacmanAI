# PacmanAI
Multiple AI approaches to playing the Pacman game:

### 1. Bellman-Ford (Winning rate: 76%)

To run the game on a small grid, run "python pacman.py -q -n 25 -p MDPAgent -l smallGrid"
To run the game on a medium grid, run "python pacman.py -q -n 25 -p MDPAgent -l mediumClassic"


### 2. Decision Tree classifier

Run "python pacman.py --pacman ClassifierAgent" to evaluate the performance

To update the training data with your own gaming moves, run "python pacman.py --p TraceAgent"

### 3. Reinforcement Learning - Q-Learning model (Winning rate: 100%)

Run "python pacman.py -p QLearnAgent -x 2000 -n 2010 -l smallGrid" for evaluate the performance



