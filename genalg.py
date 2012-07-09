# Sean Adler
# (for funnsies.)
import random

# define global vars

# room dimensions
ROWS = 20
COLUMNS = 20

# Picobot properties: number of possible states,
# directions Picobot can travel, and all possible surrounding patterns
STATES = 5
DIRECTIONS = ["N", "S", "E", "W"]
PATTERNS = ["xxxx", "Nxxx", "NExx", "NxWx", "xxxS", "xExS", "xxWS", "xExx", "xxWx"]

# Number of trials we run for each program to measure fitness 
TRIALS = 20
# Fraction of programs we will mate
TOPFRACTION = 0.2
# Fraction of programs we will mutate
MUTATIONRATE = 0.05

class Program:
    """Represents a Picobot program with its ruleset."""
    
    def __init__(self):
        """Constructs a Picobot program with an empty ruleset (dictionary)."""
        self.rulesDict = {}

    def __repr__(self):
        """Returns a string of the program's ruleset in Picobot-friendly form.
            Copy & paste any ruleset into http://www.cs.hmc.edu/picobot/ and test it!"""
        statePatternList = self.rulesDict.keys()
        statePatternList.sort()
        statePatternString = ''
        for key in statePatternList:
            statePatternString += str(key)[1] + " " + str(key)[5:9] + " -> " + str(self.rulesDict[key])[2:3] + str(self.rulesDict[key])[5:-1]
            statePatternString += '\n'
        return statePatternString
        
    def randomize(self):
        """Generates a random set of rules for self.rulesDict"""
        for state in range(STATES):
            for pattern in PATTERNS:
                # don't move Picobot into walls
                mutableDirections = ['N', 'S', 'E', 'W']
                for direction in DIRECTIONS:
                    if direction in pattern:
                        mutableDirections.remove(direction)
                        
                self.rulesDict[state, pattern] = (random.choice(mutableDirections), random.randint(0, STATES-1))
                
    def getMove(self, state, pattern):
        """Takes a state number and pattern and returns the next move and pattern."""
        return self.rulesDict[state, pattern]

    def mutate(self):
        """Chooses a single rule at random to change its move and state."""
        mutableDirs = ["N", "S", "E", "W"]
        state = random.randint(0, STATES-1)
        pattern = random.choice(PATTERNS)
        # again, we really don't want Picobot to move INTO a wall. touching walls is fine.
        for direction in DIRECTIONS:
            if direction in pattern:
                mutableDirs.remove(direction)
                
        self.rulesDict[state, pattern] = (random.choice(mutableDirs), random.randint(0, STATES-1))

    def crossover(self, other):
        """Takes another Program as input and returns a new
            offspring Program with mixed rules from its parents.
            A random Picobot state 'crossover' is chosen to split the rules
            passed on by each parent."""
        crossState = random.randint(0, STATES-1)
        child = Program()
        for state, rule in self.rulesDict:
            if state <= crossState:
                child.rulesDict[state, rule] = self.rulesDict[state, rule]
            else:
                child.rulesDict[state, rule] = other.rulesDict[state, rule]
        return child

class Picobot:
    """Represents a Picobot robot with its position in a square room.
        Also holds a specific Picobot ruleset."""
    def __init__(self, picobotrow, picobotcol, program):
        self.state = 0
        self.picobotrow = picobotrow
        self.picobotcol = picobotcol
        self.program = program

        self.array = [] # This is Picobot's conception of the room!
        for r in range(ROWS):  # global variable ROWS
            row = []  # Start with an empty row
            for c in range(COLUMNS): # global variable COLUMNS
                row.append(' ') # Empty cell represented by ' '
            self.array.append(row)  # add each row to the array
        # mark starting location
        self.array[self.picobotrow][self.picobotcol] = 'P'
        
    def __repr__(self):
        """Returns a string that shows the maze. P represents Picobot and
            . represents a previously visited location."""
        mazeString = ''
        for row in range(ROWS):
            mazeString += '|'
            for col in range(COLUMNS):
                mazeString += self.array[row][col]
            mazeString += '|' + '\n'
        return mazeString

    def step(self):
        # mark visited location before we move Picobot anywhere
        self.array[self.picobotrow][self.picobotcol] = '.'
        
        # moveTuple is Picobot's next move
        if self.picobotrow == 0:
            if self.picobotcol == 0:
                moveTuple = self.program.getMove(self.state, "NxWx")
            elif self.picobotcol == COLUMNS-1:
                moveTuple = self.program.getMove(self.state, "NExx")
            else:
                moveTuple = self.program.getMove(self.state, "Nxxx")
                
        elif self.picobotrow == ROWS-1:
            if self.picobotcol == 0:
                moveTuple = self.program.getMove(self.state, "xxWS")
            elif self.picobotcol == COLUMNS-1:
                moveTuple = self.program.getMove(self.state, "xExS")
            else:
                moveTuple = self.program.getMove(self.state, "xxxS")

        else:
            if self.picobotcol == 0:
                moveTuple = self.program.getMove(self.state, "xxWx")
            elif self.picobotcol == COLUMNS-1:
                moveTuple = self.program.getMove(self.state, "xExx")
            else:
                moveTuple = self.program.getMove(self.state, "xxxx")

        self.state = moveTuple[1]

        # actually move Picobot now
        if moveTuple[0] == 'N':
            self.picobotrow -= 1
        elif moveTuple[0] == 'E':
            self.picobotcol += 1
        elif moveTuple[0] == 'W':
            self.picobotcol -= 1
        else:
            self.picobotrow += 1

        # mark current location
        self.array[self.picobotrow][self.picobotcol] = 'P'
            
    def run(self, steps):
        """Takes number of steps as input and moves Picobot by that amount."""
        for s in range(steps):
            self.step()


### Done with class methods. Now we need functions to run the simulation.

def massCreate(popsize):
    """Takes an integer and returns a list containing the specified
        amount of randomly-generated Picobot programs."""
    progList = []
    for x in range(popsize):
        prog = Program()
        prog.randomize()
        progList.append(prog)
    return progList

def evaluateFitness(program, trials, steps):
    """Takes as input a Picobot program and two ints.
        'trials' specifies the number of random starting points to test Picobot from.
        'steps' specifies how many steps Picobot takes."""
    cellsVisited = 0
    averageVisited = 0
    for x in range(trials):
        pico = Picobot(random.randint(0,ROWS-1), random.randint(0,COLUMNS-1), program)
        pico.run(steps)
        for row in range(ROWS):
            for col in range(COLUMNS):
                if pico.array[row][col] == '.':
                    cellsVisited += 1
    # average all trials
    averageVisited = float(cellsVisited) / trials
    # divide by total cells in map
    return averageVisited / (ROWS*COLUMNS)

def GA(popsize, generations):
    """Runs a breeding/mutation simulation. Each generation is of size 'popsize'.
        'generations' specifies how many times in a row we breed/mutate.
        Prints the best program after all generations are simulated."""
    fitnessList = []
    avgFitness = 0
    generationCount = 0
    # create initial generation
    progList = massCreate(popsize)
    # loop over remaining generations
    while generationCount != generations:
        avgFitness = 0
        fitnessList = []
        # evaluate fitness of each program and store results with programs in a list
        for program in progList:
            fitnessList.append((evaluateFitness(program, TRIALS, ROWS*COLUMNS*2), program))
        fitnessList.sort() # sort by first element of tuple -- fitness
        fitnessList.reverse() # get descending order
        # calculate average fitness of generation
        avgFitness = 0
        for program in fitnessList:
            avgFitness += program[0]
        avgFitness /= popsize
        # get #1 top performer
        print "GENERATION " + str(generationCount)
        print "\tAverage Program: " + str(avgFitness)
        print "\tBest Program: " + str(max(fitnessList)[0])

        # get top performers -- cutoff is determined by global var TOPFRACTION
        topFitness = fitnessList[0:int(len(fitnessList)*TOPFRACTION)]

        # breed programs to create new generation of size 'popsize'
        newPopulation = []
        while len(newPopulation) != popsize:
            daddyProgram = random.choice(topFitness)[1]
            mommyProgram = random.choice(topFitness)[1]
            childProgram = daddyProgram.crossover(mommyProgram)
            newPopulation.append(childProgram)

        # mutate new population according to global MUTATIONRATE
        desiredMutations = int(popsize * MUTATIONRATE)
        mutationCount = 0
        while mutationCount != desiredMutations:
            newPopulation[random.randint(0, popsize-1)].mutate()
            mutationCount += 1

        progList = newPopulation
        generationCount += 1
    print
    print "Master Program from " + str(generations) + " generations of breeding: "
    print "\tFitness: " + str(max(fitnessList)[0])
    print
    # return the Master Program and HOOK IT UP TO SKYNET
    masterProgram = max(fitnessList)[1]
    return masterProgram
