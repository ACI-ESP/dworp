import argparse
import dworp
import logging
import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


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
        if self.rng.uniform() < 0.5:
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

    def move(self, agent):
        x1 = x2 = agent.x
        y1 = y2 = agent.y
        while self.grid.occupied(x2, y2):
            x2 = self.rng.randint(0, self.grid.width)
            y2 = self.rng.randint(0, self.grid.height)
        self.grid.move(x1, y1, x2, y2)
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


class SegregationSimulation(dworp.TwoStageSimulation):
    """Simulation with two stages (moving and then happiness test)"""
    def __init__(self, params, observer):
        self.params = params
        self.rng = np.random.RandomState(params.seed)
        factory = HouseholdFactory(self.rng, params.similarity, params.colors[0], params.colors[1])
        time = dworp.InfiniteTime()
        scheduler = dworp.RandomOrderScheduler(self.rng)
        terminator = SegTerminator()

        agents = []
        grid = dworp.Grid(params.grid_width, params.grid_height)
        env = SegregationEnvironment(grid, self.rng)
        for x in range(params.grid_width):
            for y in range(params.grid_height):
                if self.rng.uniform() < params.density:
                    agent = factory.create(x, y)
                    grid.set(agent, x, y)
                    agents.append(agent)

        super().__init__(agents, env, time, scheduler, observer, terminator)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)

    # parse command line
    parser = argparse.ArgumentParser()
    parser.add_argument("--density", help="density of agents (1-99)", default=95, type=int)
    parser.add_argument("--similar", help="desired similarity (0-100)", default=30, type=int)
    parser.add_argument("--size", help="grid size formatted as XXXxYYY", default="50x50")
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
        HeatmapPlotObserver(colors),
        dworp.PauseObserver(delay=1, start=True, matplotlib=True)
    )
    sim = SegregationSimulation(params, observer)
    sim.run()
