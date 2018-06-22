#All this code is just a modified version of segregation.py to simulate a fake disease instead
import argparse
import dworp
import dworp.plot
import logging
import numpy as np
import sys
import random
try:
    import pygame
except ImportError:
    # vis will be turned off
    pass

"""This is just a simulation I made off of a fake disease. It is not meant to be realistic, as coding one
that follows an established model for disease spread seems to be outside of my current programming and mathematical
abilities. If you would like to read about the SIR model for disease spread, a pretty good article can be found on
the MAA website. https://www.maa.org/press/periodicals/loci/joma/the-sir-model-for-spread-of-disease-introduction"""

class Household(dworp.Agent):
    def __init__(self, agent_id, color, x, y, similarity,):
        super().__init__(agent_id, 0)
        self.color = color
        self.x = x
        self.y = y
        self.healthy = None
        self.similarity = similarity

    def __repr__(self):
        return "Health ({}, {}, {}, {}), Healthy? = {}".format(self.agent_id, self.color, self.x, self.y, self.healthy)

    def init(self, now, env):
        if self.color == "green": #Green means healthy
            self.healthy = True
        elif self.color == "blue": #Blue means recovered from the illness, which makes them slightly less susceptible to infection
            self.healthy = True
        elif self.color == "orange": #Orange represents infected
            self.healthy = False
        elif self.color == "black": #Black represents death
            self.healthy = False

    def step(self, now, env):
        if self.color == "green":
            if not self.check_health(env):
                if random.randint(300,400) <= 375: #if near multiple infected, there is a 75%ish chance of infection
                    self.color = 'orange'
        if self.color == "orange": #if infected, there is a 20%ish chance of turning blue (cured)
            if random.randint(0,100) <= 20:
                self.color = "blue"
            elif random.randint(500,599) == 500: #1%ish chance of death
                self.color = "black"
        if self.color == "blue": #50%ish chance of being infected again
            if random.randint(200,300) <= 250:
                self.color = "orange"


    def complete(self, now, env):
        if self.color == "green":
            return True
        elif self.color == "blue":
            return True
        elif self.color == "orange":
            return False
        elif self.color == "black":
            return False

    def check_health(self, env):
        neighbors = env.grid.neighbors(self.x, self.y)
        if self.color == "blue" or self.color == "green":
            num_healthy = sum([neighbor.color == "green" for neighbor in neighbors]) + sum([neighbor.color == "blue" for neighbor in neighbors])
            return num_healthy >= 5
        elif self.color == "orange":
            return False
        elif self.color == "black":
            return False


class SubjectAssigner:
    def __init__(self, rng, color1, color2, color3, color4):
        self.rng = rng
        self.color1 = color1
        self.color2 = color2
        self.color3 = color3
        self.color4 = color4

    def assign(self):
        if self.rng.uniform() < 0.88:
            return self.color3
        else:
            return self.color2


class ThingFactory:
    def __init__(self, rng, similarity, color1, color2, color3, color4):
        self.namer = dworp.IdentifierHelper.get()
        self.similarity = similarity
        self.colorer = SubjectAssigner(rng, color1, color2, color3, color4)

    def create(self, x, y):
        return Household(next(self.namer), self.colorer.assign(), x, y, self.similarity)


class TheEnvironment(dworp.Environment):
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

    def step(self, new_time, agents):
        pass


class ThingObserver(dworp.Observer):
    def start(self, now, agents, env):
        print("STARTING DISEASE SIMULATION\nStep {}: {}% agents healthy\n{}% agents infected\n{}% agents dead".format(now, self.get_health(agents),
        self.get_infected(agents), self.get_dead(agents)))

    def step(self, now, agents, env):
        print("\nStep {}: {}% agents healthy\n{}% agents infected\n{}% agents dead".format(now, self.get_health(agents),
        self.get_infected(agents), self.get_dead(agents)))

    def stop(self, now, agents,env):
        print("\nStep {}: {}% agents healthy\n{}% agents infected\n{}% agents dead\nENDING SIMULATION".format(now, self.get_health(agents),
        self.get_infected(agents), self.get_dead(agents)))

    @staticmethod
    def get_health(agents):
        num_health = sum(agent.color == "green" for agent in agents) + sum(agent.color == "blue" for agent in agents)
        return 100 * num_health / float(len(agents))

    @staticmethod
    def get_infected(agents):
        num_infected = sum(agent.color == "orange" for agent in agents)
        return 100 * num_infected / float(len(agents))

    @staticmethod
    def get_dead(agents):
        num_dead = sum(agent.color == "black" for agent in agents)
        return 100 * num_dead / float(len(agents))
    @staticmethod
    def number_green(agents):
        number_green = sum(agent.color == "green" for agent in agents)
        return number_green

class TheTerminator(dworp.Terminator):
    def test(selfself, now, agents, env):
        if ThingObserver.number_green(agents) <= 0:
            return True
        else:
            return False
    #The function terminates after all the green households are gone because otherwise it takes too long

class PyGameRenderer(dworp.Observer):
    def __init__(self, size, zoom, fps):
        self.zoom = zoom
        self.fps = fps
        self.width = size[0]
        self.height = size[1]

        pygame.init()
        pygame.display.set_caption("Spread of Disease")
        self.screen = pygame.display.set_mode((self.zoom * self.width, self.zoom * self.height))
        self.background = pygame.Surface((self.screen.get_size()))
        self.background = self.background.convert()
        self.clock = pygame.time.Clock()

    def start(self, start_time, agents, env):
        self.draw(agents)

    def step(self, now, agents, env):
        self.draw(agents)

    def stop(self, now, agents, env):
        pygame.quit()

    def draw(self, agents):
        side = self.zoom - 1
        self.background.fill((255, 255, 255))
        for agent in agents:
            x = self.zoom * agent.x
            y = self.zoom * agent.y
            if agent.color == "orange":
                color = (255, 128, 0)
            elif agent.color == "blue":
                color = (0, 0, 255)
            elif agent.color == "green":
                color = (0, 255, 0)
            elif agent.color == "black":
                color = (0, 0, 0)
            pygame.draw.rect(self.background, color, (x, y, side, side), 0)
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        self.clock.tick(self.fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()


class DiseaseParams:
    """Container for simulation parameters"""
    def __init__(self, density, similarity, grid_size, seed, color):
        self.density = density
        self.similarity = similarity
        self.grid_width = grid_size[0]
        self.grid_height = grid_size[1]
        self.seed = seed
        self.color = color


class DiseaseSimulation(dworp.TwoStageSimulation):
    """Simulation with two stages (moving and then happiness test)"""
    def __init__(self, params, observer):
        self.params = params
        self.rng = np.random.RandomState(params.seed)
        factory = ThingFactory(self.rng, params.similarity, params.color[0], params.color[1], params.color[2], params.color[3])
        time = dworp.InfiniteTime()
        scheduler = dworp.RandomOrderScheduler(self.rng)
        terminator = TheTerminator()

        agents = []
        grid = dworp.Grid(params.grid_width, params.grid_height)
        env = TheEnvironment(grid, self.rng)
        for x in range(params.grid_width):
            for y in range(params.grid_height):
                if self.rng.uniform() < params.density:
                    agent = factory.create(x, y)
                    grid.add(agent, x, y)
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
    parser.add_argument("--fps", help="frames per second", default="2", type=int)
    parser.add_argument("--no-vis", dest='vis', action='store_false')
    parser.set_defaults(vis=True)
    args = parser.parse_args()

    # prepare parameters of simulation
    assert(1 <= args.density <= 99)
    assert(0 <= args.similar <= 100)
    density = args.density / float(100)
    similarity = args.similar / float(100)
    grid_size = [int(dim) for dim in args.size.split("x")]
    seed = args.seed
    vis_flag = args.vis and 'pygame' in sys.modules
    # vis does not support different colors
    colors = ["blue", "orange", "green", "black"]
    params = DiseaseParams(density, similarity, grid_size, seed, colors)

    # create and run one realization of the simulation
    observer = dworp.ChainedObserver(
        ThingObserver(),
    )
    if vis_flag:
        observer.append(dworp.PauseAtEndObserver(3))
        observer.append(PyGameRenderer(grid_size, 10, args.fps))
    sim = DiseaseSimulation(params, observer)
    sim.run()
