from sre_parse import State
import sys

import puzz
import pdqpq


GOAL_STATE = puzz.EightPuzzleBoard("012345678")


def solve_puzzle(start_state, flavor):
    """Perform a search to find a solution to a puzzle.
    
    Args:
        start_state (EightPuzzleBoard): the start state for the search
        flavor (str): tag that indicate which type of search to run.  Can be one of the following:
            'bfs' - breadth-first search
            'ucost' - uniform-cost search
            'greedy-h1' - Greedy best-first search using a misplaced tile count heuristic
            'greedy-h2' - Greedy best-first search using a Manhattan distance heuristic
            'greedy-h3' - Greedy best-first search using a weighted Manhattan distance heuristic
            'astar-h1' - A* search using a misplaced tile count heuristic
            'astar-h2' - A* search using a Manhattan distance heuristic
            'astar-h3' - A* search using a weighted Manhattan distance heuristic
    
    Returns: 
        A dictionary containing describing the search performed, containing the following entries:
        'path' - list of 2-tuples representing the path from the start to the goal state (both 
            included).  Each entry is a (str, EightPuzzleBoard) pair indicating the move and 
            resulting successor state for each action.  Omitted if the search fails.
        'path_cost' - the total cost of the path, taking into account the costs associated with 
            each state transition.  Omitted if the search fails.
        'frontier_count' - the number of unique states added to the search frontier at any point 
            during the search.
        'expanded_count' - the number of unique states removed from the frontier and expanded 
            (successors generated)

    """
    if flavor.find('-') > -1:
        strat, heur = flavor.split('-')
    else:
        strat, heur = flavor, None

    if strat == 'bfs':
        return BreadthFirstSolver(GOAL_STATE).solve(start_state)
    elif strat == 'ucost':
        return UCSSolver(GOAL_STATE).solve(start_state)
        # raise NotImplementedError(strat + ' not implemented yet')  # delete this line!
    elif strat == 'greedy':
        if heur == 'h1':
            return GreedyBestFirstSolver(GOAL_STATE).solve(start_state, 'h1')
        elif heur == 'h2':
            return GreedyBestFirstSolver(GOAL_STATE).solve(start_state, 'h2')
        else:
            return GreedyBestFirstSolver(GOAL_STATE).solve(start_state, 'h3')
    elif strat == 'astar':
        if heur == 'h1':
            return AstarSolver(GOAL_STATE).solve(start_state, 'h1')
        elif heur == 'h2':
            return AstarSolver(GOAL_STATE).solve(start_state, 'h2')
        else:
            return AstarSolver(GOAL_STATE).solve(start_state, 'h3')
    else:
        raise ValueError("Unknown search flavor '{}'".format(flavor))


def get_test_puzzles():
    """Return sample start states for testing the search strategies.
    
    Returns:
        A tuple containing three EightPuzzleBoard objects representing start states that have an
        optimal solution path length of 3-5, 10-15, and >=25 respectively.
    
    """ 
    #
    x = puzz.EightPuzzleBoard("125340678")
    y = puzz.EightPuzzleBoard("541632078")
    z = puzz.EightPuzzleBoard("235104867")
    #    
    return (x,y,z)  # fix this line!


def print_table(flav__results, include_path=False):
    """Print out a comparison of search strategy results.

    Args:
        flav__results (dictionary): a dictionary mapping search flavor tags result statistics. See
            solve_puzzle() for detail.
        include_path (bool): indicates whether to include the actual solution paths in the table

    """
    result_tups = sorted(flav__results.items())
    c = len(result_tups)
    na = "{:>12}".format("n/a")
    rows = [  # abandon all hope ye who try to modify the table formatting code...
        "flavor  " + "".join([ "{:>12}".format(tag) for tag, _ in result_tups]),
        "--------" + ("  " + "-"*10)*c,
        "length  " + "".join([ "{:>12}".format(len(res['path'])) if 'path' in res else na 
                                for _, res in result_tups ]),
        "cost    " + "".join([ "{:>12,}".format(res['path_cost']) if 'path_cost' in res else na 
                                for _, res in result_tups ]),
        "frontier" + ("{:>12,}" * c).format(*[res['frontier_count'] for _, res in result_tups]),
        "expanded" + ("{:>12,}" * c).format(*[res['expanded_count'] for _, res in result_tups])
    ]
    if include_path:
        rows.append("path")
        longest_path = max([ len(res['path']) for _, res in result_tups if 'path' in res ])
        print("longest", longest_path)
        for i in range(longest_path):
            row = "        "
            for _, res in result_tups:
                if len(res.get('path', [])) > i:
                    move, state = res['path'][i]
                    row += " " + move[0] + " " + str(state)
                else:
                    row += " "*12
            rows.append(row)
    print("\n" + "\n".join(rows), "\n")


class PuzzleSolver(object):
    """Base class for 8-puzzle solver."""

    def __init__(self, goal_state):
        self.parents = {}  # state -> parent_state
        self.expanded_count = 0
        self.frontier_count = 0
        self.goal = goal_state

    def get_path(self, state):
        """Return the solution path from the start state of the search to a target.
        
        Results are obtained by retracing the path backwards through the parent tree to the start
        state for the search at the root.
        
        Args:
            state (EightPuzzleBoard): target state in the search tree
        
        Returns:
            A list of EightPuzzleBoard objects representing the path from the start state to the
            target state

        """
        path = []
        while state is not None:
            path.append(state)
            state = self.parents[state]
        path.reverse()
        return path

    def get_cost(self, state): 
        """Calculate the path cost from start state to a target state.
        
        Transition costs between states are equal to the square of the number on the tile that 
        was moved. 

        Args:
            state (EightPuzzleBoard): target state in the search tree
        
        Returns:
            Integer indicating the cost of the solution path

        """
        cost = 0
        path = self.get_path(state)
        for i in range(1, len(path)):
            x, y = path[i-1].find(None)  # the most recently moved tile leaves the blank behind
            tile = path[i].get_tile(x, y)        
            cost += int(tile)**2
        return cost

    def get_results_dict(self, state):
        """Construct the output dictionary for solve_puzzle()
        
        Args:
            state (EightPuzzleBoard): final state in the search tree
        
        Returns:
            A dictionary describing the search performed (see solve_puzzle())

        """
        results = {}
        results['frontier_count'] = self.frontier_count
        results['expanded_count'] = self.expanded_count
        if state:
            results['path_cost'] = self.get_cost(state)
            path = self.get_path(state)
            moves = ['start'] + [ path[i-1].get_move(path[i]) for i in range(1, len(path)) ]
            results['path'] = list(zip(moves, path))
        return results

    def solve(self, start_state):
        """Carry out the search for a solution path to the goal state.
        
        Args:
            start_state (EightPuzzleBoard): start state for the search 
        
        Returns:
            A dictionary describing the search from the start state to the goal state.

        """
        raise NotImplementedError('Classed inheriting from PuzzleSolver must implement solve()')
        

class BreadthFirstSolver(PuzzleSolver):
    """Implementation of Breadth-First Search based on PuzzleSolver"""

    def __init__(self, goal_state):
        self.frontier = pdqpq.FifoQueue()
        self.explored = set()
        super().__init__(goal_state)

    def add_to_frontier(self, node):
        """Add state to frontier and increase the frontier count."""
        self.frontier.add(node)
        self.frontier_count += 1

    def expand_node(self, node):
        """Get the next state from the frontier and increase the expanded count."""
        self.explored.add(node)
        self.expanded_count += 1
        return node.successors()

    def solve(self, start_state):
        self.parents[start_state] = None
        self.add_to_frontier(start_state)

        if start_state == self.goal:  # edge case        
            return self.get_results_dict(start_state)

        while not self.frontier.is_empty():
            node = self.frontier.pop()  # get the next node in the frontier queue
            succs = self.expand_node(node)

            for move, succ in succs.items():
                if (succ not in self.frontier) and (succ not in self.explored):
                    self.parents[succ] = node

                    # BFS checks for goal state _before_ adding to frontier
                    if succ == self.goal:
                        return self.get_results_dict(succ)
                    else:
                        self.add_to_frontier(succ)

        # if we get here, the search failed
        return self.get_results_dict(None)


class UCSSolver(PuzzleSolver):  # the cost of moving from one state to the next is equal to the square of the number on the tile that gets shifted.
    """Implementation of Uniform Cost Search based on PuzzleSolver"""

    def __init__(self, goal_state):  
        self.frontier = pdqpq.PriorityQueue()
        self.explored = set()
        super().__init__(goal_state)

    def add_to_frontier(self, node, cost=0): 
        """Add state to frontier and increase the frontier count."""
        self.frontier.add(node, cost)
        self.frontier_count += 1

    def expand_node(self, node): 
        """Get the next state from the frontier and increase the expanded count."""
        self.explored.add(node)
        self.expanded_count += 1
        return node.successors()
        
    def solve(self, start_state):
        self.parents[start_state] = None
        self.add_to_frontier(start_state)

        if start_state == self.goal:  # edge case
            return self.get_results_dict(start_state)

        while not self.frontier.is_empty():  # iterate through frontier of states
            node = self.frontier.peek(None)[0]  # get the next node in the frontier queue

            if node == self.goal:  # checks for goal state right after pop()
                return self.get_results_dict(node)

            succs = self.expand_node(node)  # puts all expanded nodes into succ and adds them to explored

            for move, succ in succs.items():  # e.g. 'up', 012345678
                if (succ not in self.frontier) and (succ not in self.explored):  # if (n not in frontier) and (n not in explored): update parent and add to frontier
                    self.parents[succ] = node
                    self.add_to_frontier(succ, self.frontier.peek(None)[1] + self.get_cost(succ))  
                elif (succ in self.frontier):  # if already in frontier: store old parent in temp variable, update parent
                    oldParent = self.parents[succ]  
                    self.parents[succ] = node
                    if (self.frontier.get(succ) > self.frontier.peek(None)[1] + self.get_cost(succ)): # if we need to update
                        self.frontier.add(succ, self.frontier.peek(None)[1] + self.get_cost(succ))  # update
                    else:  # no need to update
                        self.parents[succ] = oldParent  # restore old parent
            self.frontier.pop()  # remove node from frontier

        # if we get here, the search failed
        return self.get_results_dict(None)


class GreedyBestFirstSolver(PuzzleSolver):
    """Implementation of Greedy Best-First Search based on PuzzleSolver"""

    def __init__(self, goal_state):
        self.frontier = pdqpq.PriorityQueue()
        self.explored = set()      #convert iterables
        super(GreedyBestFirstSolver, self).__init__(goal_state)

    def add_to_frontier(self, node, priority=0):    # need to get heuristic/priority, and add as a param
        """Add state to frontier and increase the frontier count."""
        self.frontier.add(node, priority)
        self.frontier_count += 1

    def expand_node(self, node):
        """Get the next state from the frontier and increase the expanded count."""
        self.explored.add(node)
        self.expanded_count += 1
        return node.successors()

    def h1(self, state):
        """ count # of misplaced tiles in a successor state"""
        incorrect = 0  # counter variable
        for i in range(3):
            for j in range(3):  # iterate through all coordinates: (0,0), (0,1), (0,2), (1,0), etc.
                if state.get_tile(i, j) != "0":  # do not account for empty square
                    if state.get_tile(i, j) != self.goal.get_tile(i, j):  # if wrong square value: 
                        incorrect += 1  # increment counter
        return incorrect        

    def h2(self, state):
        """heuristic based on the Manhattan distance of the tiles on the board"""
        # coords is a dict with the correct coords of each tile in the goal state
        coords = {0: (0, 2), 1: (1, 2), 2: (2, 2), 3: (0, 1), 4: (1, 1), 5: (2, 1), 6: (0, 0), 7: (1, 0), 8: (2, 0)}
        distance = 0  # counter
        for i in range(3):
            for j in range(3):  # iterate through all coordinates: (0,0), (0,1), (0,2), (1,0), etc.
                if state.get_tile(i, j) != "0":  # do not account for empty square
                    currTile = state.get_tile(i, j)
                    if currTile != self.goal.get_tile(i, j):  # if wrong square value: calculate how far away from correct space
                        x = coords[int(currTile)][0]
                        y = coords[int(currTile)][1]
                        distance += (abs(x - i) + abs(y - j))  # increment counter
        return distance

    def h3(self, state):
        """heuristic based on the weighted Manhattan distance of the tiles on the board (Manhatten Distance * (Tile Value ** 2))"""
        # coords is a dict with the correct coords of each tile in the goal state
        coords = {0: (0, 2), 1: (1, 2), 2: (2, 2), 3: (0, 1), 4: (1, 1), 5: (2, 1), 6: (0, 0), 7: (1, 0), 8: (2, 0)}
        distance = 0  # counter
        for i in range(3):
            for j in range(3):  # iterate through all coordinates: (0,0), (0,1), (0,2), (1,0), etc.
                if state.get_tile(i, j) != "0":  # do not account for empty square
                    currTile = state.get_tile(i, j)
                    if currTile != self.goal.get_tile(i, j):  # if wrong square value: calculate how far away from correct space and multiply by tile value squared
                        weight = int(currTile)**2
                        x = coords[int(currTile)][0]
                        y = coords[int(currTile)][1]
                        distance += ((abs(x - i) + abs(y - j))*weight)  # increment counter
        return distance


    def solve(self, start_state, h):         # h: heuristic type
        self.parents[start_state] = None
        self.add_to_frontier(start_state)

        if start_state == self.goal:  # edge case
            return self.get_results_dict(start_state)

        while not self.frontier.is_empty():  # iterate through frontier of states
            node = self.frontier.peek(None)[0]  # get the next node in the frontier queue

            if node == self.goal:  # checks for goal state right after pop()
                return self.get_results_dict(node)

            succs = self.expand_node(node)  # puts all expanded nodes into succ and adds them to explored

            for move, succ in succs.items():  # e.g. 'up', 012345678, calculate heuristic value
                if h == 'h1':
                    cost = self.h1(succ)
                elif h == 'h2':
                    cost = self.h2(succ)
                elif h == 'h3':
                    cost = self.h3(succ)

                if (succ not in self.frontier) and (succ not in self.explored):  # if (n not in frontier) and (n not in explored): update parent and add to frontier
                    self.parents[succ] = node
                    self.add_to_frontier(succ, cost)
                elif (succ in self.frontier):  # else if (n in frontier): store old parent in temp variable, update parent
                    oldParent = self.parents[succ]
                    self.parents[succ] = node
                    if (self.frontier.get(succ) > cost):  # if we need to update
                        self.frontier.add(succ, cost)  # update
                    else:  # do not need to update
                        self.parents[succ] = oldParent  # restore old parent value

        # search failed if reached
        return self.get_results_dict(None)


class AstarSolver(PuzzleSolver):  # the cost of moving from one state to the next is equal to the square of the number on the tile that gets shifted.
    """Implementation of Uniform Cost Search based on PuzzleSolver"""

    def __init__(self, goal_state):  # Done
        self.frontier = pdqpq.PriorityQueue()
        self.explored = set()
        super().__init__(goal_state)

    def add_to_frontier(self, node, cost=0):  # Done
        """Add state to frontier and increase the frontier count."""
        self.frontier.add(node, cost)
        self.frontier_count += 1

    def expand_node(self, node):  # Done
        """Get the next state from the frontier and increase the expanded count."""
        self.explored.add(node)
        self.expanded_count += 1
        return node.successors()

    def h1(self, state):
        """ count # of misplaced tiles in a successor state"""
        incorrect = 0  # counter variable
        for i in range(3):
            for j in range(3):  # iterate through all coordinates: (0,0), (0,1), (0,2), (1,0), etc.
                if state.get_tile(i, j) != "0":  # do not account for empty square
                    if state.get_tile(i, j) != self.goal.get_tile(i, j):  # if wrong square value: 
                        incorrect += 1  # increment counter
        return incorrect        

    def h2(self, state):
        """heuristic based on the Manhattan distance of the tiles on the board"""
        # coords is a dict with the correct coords of each tile in the goal state
        coords = {0: (0, 2), 1: (1, 2), 2: (2, 2), 3: (0, 1), 4: (1, 1), 5: (2, 1), 6: (0, 0), 7: (1, 0), 8: (2, 0)}
        distance = 0  # counter
        for i in range(3):
            for j in range(3):  # iterate through all coordinates: (0,0), (0,1), (0,2), (1,0), etc.
                if state.get_tile(i, j) != "0":  # do not account for empty square
                    currTile = state.get_tile(i, j)
                    if currTile != self.goal.get_tile(i, j):  # if wrong square value: calculate how far away from correct space
                        x = coords[int(currTile)][0]
                        y = coords[int(currTile)][1]
                        distance += (abs(x - i) + abs(y - j))  # increment counter
        return distance

    def h3(self, state):
        """heuristic based on the weighted Manhattan distance of the tiles on the board (Manhatten Distance * (Tile Value ** 2))"""
        # coords is a dict with the correct coords of each tile in the goal state
        coords = {0: (0, 2), 1: (1, 2), 2: (2, 2), 3: (0, 1), 4: (1, 1), 5: (2, 1), 6: (0, 0), 7: (1, 0), 8: (2, 0)}
        distance = 0  # counter
        for i in range(3):
            for j in range(3):  # iterate through all coordinates: (0,0), (0,1), (0,2), (1,0), etc.
                if state.get_tile(i, j) != "0":  # do not account for empty square
                    currTile = state.get_tile(i, j)
                    if currTile != self.goal.get_tile(i, j):  # if wrong square value: calculate how far away from correct space and multiply by tile value squared
                        weight = int(currTile)**2
                        x = coords[int(currTile)][0]
                        y = coords[int(currTile)][1]
                        distance += ((abs(x - i) + abs(y - j))*weight)  # increment counter
        return distance

    def solve(self, start_state, h):         # h: heuristic type
        self.parents[start_state] = None
        self.add_to_frontier(start_state)

        if start_state == self.goal:  # edge case
            return self.get_results_dict(start_state)

        while not self.frontier.is_empty():  # iterate through frontier of states
            node = self.frontier.pop()  # get the next node in the frontier queue

            if node == self.goal:  # checks for goal state right after pop()
                return self.get_results_dict(node)

            succs = self.expand_node(node)  # puts all expanded nodes into succ and adds them to explored

            for move, succ in succs.items():  # e.g. 'up', 012345678, calculate heuristic value
                if h == 'h1':
                    cost = self.h1(succ)
                elif h == 'h2':
                    cost = self.h2(succ)
                elif h == 'h3':
                    cost = self.h3(succ)

                if (succ not in self.frontier) and (succ not in self.explored):  # if (n not in frontier) and (n not in explored): update parent and add to frontier
                    self.parents[succ] = node
                    self.add_to_frontier(succ, cost+self.get_cost(succ))
                    
                elif (succ in self.frontier):  # else if (n in frontier): store old parent in temp variable, update parent
                    oldParent = self.parents[succ]
                    self.parents[succ] = node
                    
                    if (self.frontier.get(succ) > cost+self.get_cost(succ)):  # if we need to update
                        self.frontier.add(succ, cost+self.get_cost(succ)) #update
                        
                    else:  # do not need to update
                        self.parents[succ] = oldParent  # restore old frontier value

        # search failed if reached
        return self.get_results_dict(None)



############################################

if __name__ == '__main__':

    # parse the command line args
    start = puzz.EightPuzzleBoard(sys.argv[1])
    if sys.argv[2] == 'all':
        flavors = ['bfs', 'ucost', 'greedy-h1', 'greedy-h2', 
                   'greedy-h3', 'astar-h1', 'astar-h2', 'astar-h3']
    else:
        flavors = sys.argv[2:]

    # run the search(es)
    results = {}
    for flav in flavors:
        print("solving puzzle {} with {}".format(start, flav))
        results[flav] = solve_puzzle(start, flav)

    print_table(results, include_path=False)  # change to True to see the paths!


