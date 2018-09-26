# Sugarscape
#
# To run, you must install pygame:
# pip install pygame
#
# Original paper:
# Epstein, J.M. & Axtell, R. Artificial Life and Robotics (1997) 1: 33. https://doi.org/10.1007/BF02471109
#
# This reproduces the model according to NetLogo.
#
# The pygame visualization seems to have a busy wait loop which will peg a processor.
#

import argparse
import dworp
import logging
import numpy as np
import pygame
from sugarscape_map import DEFAULT_SUGAR_MAP


class Patch:
    def __init__(self, max_sugar):
        self.sugar = max_sugar
        self.max_sugar = max_sugar

    def growback(self):
        # immediate growback model
        # self.sugar = self.max_sugar

        # constant growback model
        self.sugar = min(self.sugar + 1, self.max_sugar)

    def __repr__(self):
        return 'Patch({}, {})'.format(self.sugar, self.max_sugar)


class Turtle(dworp.SelfNamingAgent):
    def __init__(self, sugar, metabolism, vision):
        super().__init__(0)

        self.sugar = sugar
        self.metabolism = metabolism
        self.vision = vision

    def step(self, now, env):
        self.move(env)
        self.eat(env)
        self.metabolize()

    def move(self, env):
        # get empty locations nearby, and their sugar & distance
        empty_locations = env.empty_locations_nearby(self, self.vision)
        sugar_by_location = {location: env.get_patch_at(location).sugar for location in empty_locations}
        distance_by_location = {location: env.distance_from(self, location) for location in empty_locations}

        # pick the best locations (the ones with the most sugar)
        max_sugar = max(sugar_by_location.values())
        best_locations = list(filter(lambda location: sugar_by_location[location] >= max_sugar, empty_locations))

        # move to the closest best location
        env.move(self, min(best_locations, key=distance_by_location.get))

    def eat(self, env):
        patch = env.get_patch_for(self)
        self.sugar += patch.sugar
        patch.sugar = 0

    def metabolize(self):
        self.sugar -= self.metabolism

    def is_dead(self):
        return self.sugar <= 0


class SugarscapeEnvironment(dworp.Environment):
    def __init__(self, sugar_map=DEFAULT_SUGAR_MAP):
        super().__init__(0)

        self.width = len(sugar_map[0])
        self.height = len(sugar_map)

        self.patch_by_location = {}
        self.agent_by_location = {}
        for x in range(self.width):
            for y in range(self.height):
                self.patch_by_location[(x, y)] = Patch(sugar_map[y][x])
                self.agent_by_location[(x, y)] = None

        self.max_sugar = max(map(lambda patch: patch.max_sugar, self.patch_by_location.values()))

        self.location_by_agent = {}

    def step(self, now, agents):
        for location in self.patch_by_location:
            self.patch_by_location[location].growback()

    def complete(self, now, agents):
        to_remove = []
        for i, agent in enumerate(agents):
            if agent.is_dead():
                to_remove.append(i)

        for i in reversed(to_remove):
            agents.pop(i)

    def is_valid_location(self, location):
        return location in self.patch_by_location

    def move(self, agent, location):
        if agent in self.location_by_agent:
            self.agent_by_location[self.location_by_agent[agent]] = None

        self.location_by_agent[agent] = location
        self.agent_by_location[location] = agent

    def get_patch_for(self, agent):
        return self.get_patch_at(self.location_by_agent[agent])

    def get_patch_at(self, location):
        return self.patch_by_location[location]

    def distance_from(self, agent, location):
        agent_location = self.location_by_agent[agent]

        x1, y1 = agent_location
        x2, y2 = location

        return abs(x2 - x1) + abs(y2 - y1)

    def is_empty(self, location):
        return self.agent_by_location[location] is None

    def empty_locations(self):
        return list(filter(self.is_empty, self.patch_by_location))

    def empty_locations_nearby(self, agent, distance):
        x, y = self.location_by_agent[agent]

        empty_locations = [(x, y)]  # allow staying in the same spot
        for d in range(1, distance + 1):
            for neighbor in [(x + d, y), (x - d, y), (x, y + d), (x, y - d)]:
                if self.is_valid_location(neighbor) and self.is_empty(neighbor):
                    empty_locations.append(neighbor)

        return empty_locations


class SugarscapeTerminator(dworp.Terminator):
    def test(self, now, agents, env):
        return len(agents) == 0


class SugarscapeSimulation(dworp.BasicSimulation):
    def __init__(self, params, observer):
        self.rng = np.random.RandomState(params.seed)

        env = SugarscapeEnvironment()

        # construct our agents
        agents = [self.create_turtle() for _ in range(params.pop)]

        # assign them locations & add them to the environment
        for agent in agents:
            empty_locations = env.empty_locations()

            # note: can't just do self.rng.choice(empty_locations), because numpy thinks a list of tuples is
            # multi-dimensional, and rng.choice only works with 1-d arrays.
            env.move(agent, empty_locations[self.rng.choice(range(len(empty_locations)))])

        super().__init__(agents, env, dworp.InfiniteTime(), dworp.BasicScheduler(), observer, SugarscapeTerminator())

    def create_turtle(self):
        sugar = self.rng.randint(5, 25)
        metabolism = self.rng.randint(1, 4)
        vision = self.rng.randint(1, 6)
        return Turtle(sugar, metabolism, vision)


class SugarscapeObserver(dworp.Observer):
    """Writes simulation state to stdout"""

    def step(self, time, agents, env):
        if time % 100 == 0:
            print("Step {}".format(time))


class PyGameRenderer(dworp.Observer):
    def __init__(self, fps):
        self.zoom = 5
        self.fps = fps

        pygame.init()
        pygame.display.set_caption("Sugarscape")

        self.width = None
        self.height = None
        self.max_sugar = None
        self.screen = None
        self.background = None
        self.clock = pygame.time.Clock()

    def start(self, now, agents, env):
        self.width = env.width
        self.height = env.height
        self.max_sugar = env.max_sugar
        self.screen = pygame.display.set_mode((self.zoom * self.width, self.zoom * self.height))
        self.background = pygame.Surface((self.screen.get_size()))
        self.background = self.background.convert()

        self.draw(env, agents)

    def step(self, now, agents, env):
        self.draw(env, agents)

    def stop(self, now, agents, env):
        pygame.quit()

    def draw(self, env, agents):
        radius = self.zoom // 2
        offset = radius
        self.background.fill((0, 0, 0))

        for (x, y), patch in env.patch_by_location.items():
            color = (0, round(255 * patch.sugar / self.max_sugar), 0)
            pygame.draw.rect(self.background, color, (self.zoom * x, self.zoom * y, self.zoom - 1, self.zoom - 1), 0)

        for agent in agents:
            location = env.location_by_agent[agent]
            x = round(self.zoom * location[0] + offset)
            y = round(self.zoom * location[1] + offset)
            pygame.draw.circle(self.background, (255, 255, 255), (x, y), radius)
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        self.clock.tick(self.fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)

    # parse command line
    parser = argparse.ArgumentParser()
    parser.add_argument("--pop", help="population (1-1000)", default=100, type=int)
    parser.add_argument("--fps", help="frames per second", default="20", type=int)
    parser.add_argument("--seed", help="seed of RNG", default=42, type=int)
    args = parser.parse_args()

    # validate parameters of simulation
    assert (1 <= args.pop <= 1000)

    observer = dworp.ChainedObserver(
        SugarscapeObserver(),
        PyGameRenderer(args.fps),
    )

    # create and run one realization of the simulation
    sim = SugarscapeSimulation(args, observer)
    sim.run()
