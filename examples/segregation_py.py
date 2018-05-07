import argparse
import dworp
import logging
#import numpy as np
import random
import itertools as itr
#import collections as coll


class Household(dworp.Agent):
    """Household agent for Schelling Segregation model"""
    def __init__(self, agent_id, color, x, y, similarity):
        super().__init__(agent_id, 0)
        self.color = color
        self.x = x
        self.y = y
        self.happy = None
        self.similarity = similarity

    def __repr__(self):
        return "Household({}, {}, ({},{}), happy={})".format(
            self.agent_id, self.color, self.x, self.y, self.happy)

    def init(self, start_time, env):
        self.happy = self.check_happiness(env)

    def step(self, new_time, env):
        if not self.check_happiness(env):
            env.move(self)

    def complete(self, current_time, env):
        self.happy = self.check_happiness(env)

    def check_happiness(self, env):
        """Check neighbors' color"""
        similar, total = env.grid.count_same_neighbors(self.x, self.y)
        return similar >= self.similarity * total

    def check_happiness_slow(self, env):
        """Check neighbors' color"""
        neighbors = env.grid.neighbors(self.x, self.y)
        similar = sum([neighbor.color == self.color for neighbor in neighbors])
        total = len(neighbors)
        return similar >= self.similarity * total
    


class ColorAssigner:
    """Assigns a color to a household probabilistically"""
    def __init__(self, rng, color1, color2):
        self.rng = rng
        self.color1 = color1
        self.color2 = color2

    def assign(self):
        if self.rng.uniform(0.,1.) < 0.5:
            return self.color1
        else:
            return self.color2


class HouseholdFactory:
    """Creates households as needed"""
    def __init__(self, rng, similarity, color1, color2):
        self.namer = dworp.IdentifierHelper.get()
        self.similarity = similarity
        self.colorer = ColorAssigner(rng, color1, color2)

    def create(self, x, y):
        return Household(next(self.namer), self.colorer.assign(), x, y, self.similarity)


class SegregationEnvironment(dworp.Environment):
    """Segregation environment that holds the grid"""
    def __init__(self, grid, rng):
        super().__init__(0)
        self.grid = grid
        self.rng = rng

    def move_guess_and_check(self, agent):
        x1 = x2 = agent.x
        y1 = y2 = agent.y
        while self.grid.occupied(x2, y2):
            x2 = self.rng.randint(0, self.grid.width)
            y2 = self.rng.randint(0, self.grid.height)
        self.grid.move(x1, y1, x2, y2)
        agent.x = x2
        agent.y = y2
    
    def move(self, agent):
        x2, y2 = self.rng.choice(list(self.grid.empty))
        self.grid.move(agent.x, agent.y, x2, y2)
        agent.x = x2
        agent.y = y2
        
    def init(self, start_time):
        pass

    def step(self, new_time, agents):
        pass


class SegObserver(dworp.Observer):
    """Writes simulation state to stdout"""
    def start(self, time, agents, env):
        print("Starting: {}% agents happy".format(self.get_happiness(agents)))

    def step(self, time, agents, env):
        print("Step {}: {}% agents happy".format(time, self.get_happiness(agents)))

    def done(self, agents, env):
        print("Ending: {}% agents happy".format(self.get_happiness(agents)))

    @staticmethod
    def get_happiness(agents):
        num_happy = sum(agent.happy for agent in agents)
        return 100 * num_happy / float(len(agents))


class SegTerminator(dworp.Terminator):
    """Stop when everyone is happy"""
    def test(self, time, agents, env):
        return SegObserver.get_happiness(agents) >= 100


class HeatmapPlotObserver(dworp.Observer):
    """Plot the segregration grid"""
    def __init__(self, colors):
        self.data = None
        self.colors = colors
        cmap = matplotlib.colors.ListedColormap([colors[0], "white", colors[1]])
        self.options = {
            'cmap': cmap, 'cbar': False, 'linewidths': 0.2,
            'xticklabels': False, 'yticklabels': False
        }

    def start(self, time, agents, env):
        self.data = np.zeros(env.grid.data.shape)
        plt.ion()
        self.plot(env.grid)

    def step(self, time, agents, env):
        self.plot(env.grid)

    def plot(self, grid):
        for x in range(self.data.shape[0]):
            for y in range(self.data.shape[1]):
                if grid.data[x, y] is None:
                    self.data[x, y] = 0
                elif grid.data[x, y].color == self.colors[0]:
                    self.data[x, y] = -1
                else:
                    self.data[x, y] = 1
        sns.heatmap(self.data, **self.options)


class SegregationParams:
    """Container for simulation parameters"""
    def __init__(self, density, similarity, grid_size, seed, colors):
        self.density = density
        self.similarity = similarity
        self.grid_width = grid_size[0]
        self.grid_height = grid_size[1]
        self.seed = seed
        self.colors = colors

class PYRandomOrderScheduler(dworp.Scheduler):
    """Random permutation of all agents

    Args:
        rng (numpy.random.RandomState): numpy random generator
    """
    def __init__(self, rng_perm):
        self.rng_perm = rng_perm

    def step(self, time, agents, env):
        agent_idx = list(range(len(agents)))
        self.rng_perm(agent_idx)
        return agent_idx
    
class SegregationSimulation(dworp.TwoStageSimulation):
    """Simulation with two stages (moving and then happiness test)"""
    def __init__(self, params, observer):
        self.params = params
        #self.rng = np.random.RandomState(params.seed)
        self.rng = random
        self.rng.seed(params.seed)
        factory = HouseholdFactory(self.rng, params.similarity, params.colors[0], params.colors[1])
        time = dworp.InfiniteTime()
        scheduler = PYRandomOrderScheduler(self.rng.shuffle)
        terminator = SegTerminator()

        agents = []
        grid = DictGrid(params.grid_width, params.grid_height)
        env = SegregationEnvironment(grid, self.rng)
        for x in range(params.grid_width):
            for y in range(params.grid_height):
                if self.rng.uniform(0., 1.) < params.density:
                    agent = factory.create(x, y)
                    grid.put(agent, x, y)
                    agents.append(agent)

        super().__init__(agents, env, time, scheduler, observer, terminator)


class DictGrid:
    """Two dimension grid that agents live on

    Only one agent per grid location.
    Zero-based indexing.

    Args:
        width (int): width of the grid (x dimension)
        height (int): height of the grid (y dimension)
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = {}
        self.empty = { (x,y) 
            for x,y in itr.product(range(width), range(height))
            }

    def occupied(self, x, y):
        """Does anyone live here"""
        return (x,y) in self.empty

    def put(self, agent, x, y):
        """Place an agent here
        Does not check if anyone else lives here first!
        """
        self.data[(x, y)] = agent
        self.empty.remove((x,y))

    def get(self, x, y):
        """Get the current agent that lives here (or None)"""
        return self.data.get((x, y), None)

    def remove(self, x, y):
        """Remove the agent from here"""
        self.data.pop((x, y), None)
        self.empty.add((x,y))
            
    def move(self, x1, y1, x2, y2):
        """Move an agent from location 1 to location 2
        Does not check if anyone lives at location 2!
        """
        agent = self.get(x1, y1)
        self.remove(x1, y1)
        self.put(agent, x2, y2)
        #self.data[(x2, y2)] = self.data[(x1,y1)]
        #self.remove(x1, y1)

    def neighbors(self, x, y):
        """Get the neighbor agents of this location

        Returns:
            list of agents
        """
        neighbors = []
        positions = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1)
            ]
        for position in positions:
            x1 = x + position[0]
            y1 = y + position[1]
            if 0 <= x1 < self.width and 0 <= y1 < self.height and self.occupied(x1, y1):
                neighbors.append(self.data[(x1, y1)])
        return neighbors

    def count_same_neighbors(self, x, y):
        """Get the neighbor agents of this location

        Returns:
            list of agents
        """
        ego_pos = (x,y)
        same_neighbors = 0
        total_neighbors = 0
        positions = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1)
            ]
        for position in ((x+ox, y+ox) for (ox, oy) in positions):
            #if 0 <= x1 < self.width and 0 <= y1 < self.height and self.occupied(x1, y1):
            if position in self.data:
                same_neighbors += (self.data[position].color == self.data[ego_pos].color)
                total_neighbors += 1
                
        return (same_neighbors, total_neighbors)



if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)

    # parse command line
    parser = argparse.ArgumentParser()
    parser.add_argument("--density", help="density of agents (1-99)", default=95, type=int)
    parser.add_argument("--similar", help="desired similarity (0-100)", default=30, type=int)
    parser.add_argument("--size", help="grid size formatted as XXXxYYY", default="200x200")
    parser.add_argument("--seed", help="seed of RNG", default=42, type=int)
    args = parser.parse_args()

    # prepare parameters of simulation
    assert(1 <= args.density <= 99)
    assert(0 <= args.similar <= 100)
    density = args.density / float(100)
    similarity = args.similar / float(100)
    grid_size = [int(dim) for dim in args.size.split("x")]
    seed = args.seed
    colors = ["blue", "orange"]
    params = SegregationParams(density, similarity, grid_size, seed, colors)

    # create and run one realization of the simulation
    observer = dworp.ChainedObserver(
        SegObserver(),
        #HeatmapPlotObserver(colors),
        #dworp.plot.PlotPauseObserver(delay=1, start=True)
    )
    sim = SegregationSimulation(params, observer)
    sim.run()
