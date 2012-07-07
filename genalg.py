# Sean Adler
# for funnsies.
import random
# import other packages as needed

# define global vars
ROWS = 20
COLUMNS = 20

STATES = 5
PATTERNS = ["xxxx", "Nxxx", "NExx", "NxWx", "xxxS", "xExS", "xxWS", "xExx", "xxWx"]
DIRECTIONS = ["N", "S", "E", "W"]
TOPFRACTION = 0.2
MUTATIONRATE = 0.10

class Program:
    """Represents a Picobot program (ruleset)."""
    
    def __init__(self):
        self.rulesDict = {}

    def __repr__(self):
        statePatternList = self.rulesDict.keys()
        statePatternList.sort()
        statePatternString = ''
        for key in statePatternList:
            statePatternString += str(key) + " -> " + str(self.rulesDict[key])
            statePatternString += '\n'
        return statePatternString
        
    def randomize(self):
        """Generates a random set of rules for self.rulesDict"""
        mutableDirections = ["N", "E", "W", "S"]
        for state in range(STATES):
            for pattern in PATTERNS:
                # don't try to move into walls
                mutableDirections = ["N", "E", "W", "S"]
                for direction in DIRECTIONS:
                    if direction in pattern:
                        mutableDirections.remove(direction)
                        
                self.rulesDict[state, pattern] = (random.choice(mutableDirections), random.randint(0, STATES-1))
    def getMove(self, state, pattern):
        """Takes a state number and pattern and returns the next move and pattern."""
        return self.rulesDict[state, pattern]

    def mutate(self):
        """Chooses a single rule at random to change its move and state."""
        mutableDirections = ["N", "S", "E", "W"]
        state = random.randint(0, STATES-1)
        pattern = random.choice(PATTERNS)

        for direction in mutableDirections:
            if direction in pattern:
                mutableDirections.remove(direction)
                
        self.rulesDict[state, pattern] = \
        (random.choice(mutableDirections), random.randint(0, STATES-1))

    def crossover(self, other):
        """Takes another Program as input and returns a new
            offspring Program with mixed rules from its parents.
            A random 'crossover' state is chosen to split the rules
            received by the child."""
        crossState = random.randint(0, STATES-1)
        child = Program()
        for state, rule in self.rulesDict:
            if state <= crossState:
                child.rulesDict[state, rule] = self.rulesDict[state, rule]
            else:
                child.rulesDict[state, rule] = other.rulesDict[state, rule]
        return child

class Picobot:
    """Represents a Picobot robot. Also contains Picobot environment."""
    def __init__(self, picobotrow, picobotcol, program):
        self.state = 0
        self.picobotrow = picobotrow
        self.picobotcol = picobotcol
        self.program = program

        self.array = [] # This is Picobot's self conception of the room!
        for r in range(ROWS):  # This is using the global variable ROWS
            row = []  # Start with an empty row
            for c in range(COLUMNS): # This is using the global variable COLUMNS
                row.append(' ') # Empty cell represented by ' '
            self.array.append(row)  # add that row to the array
        # mark starting location
        self.array[self.picobotrow][self.picobotcol] = 'P'

    def step(self):
        # mark visited location
        self.array[self.picobotrow][self.picobotcol] = '.'
        
        # moveTuple: picobot's next move
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
        
        if moveTuple[0] == 'N':
            self.picobotrow -= 1
        elif moveTuple[0] == 'E':
            self.picobotcol += 1
        elif moveTuple[0] == 'W':
            self.picobotcol -= 1
        elif moveTuple[0] == 'S':
            self.picobotrow += 1

        # minor bandaid to prevent out-of-bounds -- fix this for real eventually
        if self.picobotrow == ROWS:
            self.picobotrow -= 1
        if self.picobotrow == -1:
            self.picobotrow += 1
        if self.picobotcol == COLUMNS:
            self.picobotcol -= 1
        if self.picobotcol == -1:
            self.picobotcol += 1

        # mark current location
        self.array[self.picobotrow][self.picobotcol] = 'P'
            
    def run(self, steps):
        """Takes number of steps as input and moves Picobot that # of steps."""
        for s in range(steps):
            self.step()

    def __repr__(self):
        """Returns a string that shows the maze, Picobot's position,
            and . marks for visited locations in the maze."""
        mazeString = ''
        for row in range(ROWS):
            mazeString += '|'
            for col in range(COLUMNS):
                mazeString += self.array[row][col]
            mazeString += '|' + '\n'
        return mazeString

def massCreate(popsize):
    """Takes an integer and returns that many random Picobot programs."""
    progList = []
    for x in range(popsize):
        prog = Program()
        prog.randomize()
        progList.append(prog)
    return progList

def evaluateFitness(program, trials, steps):
    """Takes as input a Picobot program and two ints.
        Trials specifies the number of random starting points to be tested.
        Steps specifies the number of steps Picobot takes."""
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
    """Runs a breeding simulation for a given popsize over a given # of generations.
        Prints the fittest AI after all generations have run."""
    fitnessList = []
    avgFitness = 0
    generationCount = 0
    # create initial generation
    progList = massCreate(popsize)
    # loop over remaining generations
    while generationCount != generations:
        avgFitness = 0
        fitnessList = []
        for program in progList:
            fitnessList.append((evaluateFitness(program, 20, 800), program))
        fitnessList.sort() # sort by first element of tuple -- fitness
        fitnessList.reverse() # get descending order
        # calculate average fitness of generation
        avgFitness -= avgFitness
        for program in fitnessList:
            avgFitness += program[0]
        avgFitness /= len(fitnessList)
        # get #1 top performer
        print "Generation " + str(generationCount)
        # print "Fitness list length: " + str(len(fitnessList))
        print "\tAverage AI: " + str(avgFitness)
        print "\tTop AI: " + str(max(fitnessList)[0])

        # get top performers -- cutoff is global TOPFRACTION
        topFitness = fitnessList[0:int(len(fitnessList)*TOPFRACTION)]
        # print "TopFitness[0]: " + str(topFitness[0])

        # breed AIs to create new generation
        # generationCount += 1
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
    print "\n\n"
    print "Master AI from " + str(generations) + " generations of breeding: "
    print "\tFitness: " + str(max(fitnessList)[0])
    print str(max(fitnessList)[1])
