# Flocking
#
# To run, you must install pygame:
# pip install pygame
#
# Original paper:
# Reynolds, Craig W. "Flocks, herds and schools: A distributed behavioral model."
# ACM SIGGRAPH computer graphics. Vol. 21. No. 4. ACM, 1987.
#
# This reproduces the model according to NetLogo.
# The cohere function is likely different as is the vision parameter.
#
# The pygame visualization seems to have a busy wait loop which will peg a processor.
#

import argparse
import dworp
import logging
import math
import numpy as np
from operator import itemgetter
import pygame
import statistics
import os
import subprocess
import pdb


class Point2d:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Point2d({}, {})".format(self.x, self.y)


class Space2d:
    """2D Torus continuous space"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.agents = {}

    def add(self, agent, point):
        # does not check if this goes outside the space
        self.agents[agent] = point

    def remove(self, agent):
        del self.agents[agent]

    def move(self, agent, point):
        # does not check if this goes outside the space
        self.agents[agent] = point

    def move_by_vector(self, agent, mag, angle):
        point = self.agents[agent]
        dx = mag * math.cos(math.radians(angle))
        dy = mag * math.sin(math.radians(angle))
        point.x = (point.x + dx) % self.width
        point.y = (point.y + dy) % self.height
        return point

    def get_neighbors(self, agent, radius):
        neighbors = []
        for a, p in self.agents.items():
            if a == agent:
                continue
            if self.distance(agent.point, p) < radius:
                neighbors.append(a)
        return neighbors

    def distance(self, p1, p2):
        # wraps
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        dx2 = self.width - dx
        dy2 = self.height - dy
        dx_min = dx if abs(dx) < abs(dx2) else dx2
        dy_min = dy if abs(dy) < abs(dy2) else dy2
        return math.sqrt(dx_min * dx_min + dy_min * dy_min)


class Boid(dworp.SelfNamingAgent):
    """Bird-oid object that forms flocks"""
    def __init__(self, point, heading, params, space):
        super().__init__(0)
        self.point = point
        self.heading = heading
        self.space = space
        self.flockmates = []
        self.vision = params.vision
        self.min_separation = params.min_separation
        self.max_separate_turn = params.max_separate_turn
        self.max_align_turn = params.max_align_turn
        self.max_cohere_turn = params.max_cohere_turn

    def step(self, new_time, env):
        # calculate new heading (does not handle order of updates)
        self.flockmates = self.space.get_neighbors(self, self.vision)
        if self.flockmates:
            nn = self.find_nearest_neighbor()
            if self.space.distance(self.point, nn.point) < self.min_separation:
                self.separate(nn)
            else:
                self.align()
                self.cohere()

    def complete(self, new_time, env):
        # move forward 1 step according to heading
        self.point = self.space.move_by_vector(self, 1, self.heading)

    def separate(self, neighbor):
        # boids don't want to fly too close to each other
        self.turn_away(neighbor.heading, self.max_separate_turn)

    def align(self):
        # try to match the heading of flockmates
        self.turns_towards(self.average_flockmate_heading(), self.max_align_turn)

    def cohere(self):
        # try to fly closer together
        self.turns_towards(self.average_heading_towards_flockmates(), self.max_cohere_turn)

    def find_nearest_neighbor(self):
        distances = [self.space.distance(self.point, n.point) for n in self.flockmates]
        index = min(enumerate(distances), key=itemgetter(1))[0]
        return self.flockmates[index]

    def average_flockmate_heading(self):
        x_component = sum(math.cos(math.radians(n.heading)) for n in self.flockmates)
        y_component = sum(math.sin(math.radians(n.heading)) for n in self.flockmates)
        return math.degrees(math.atan2(y_component, x_component))

    def average_heading_towards_flockmates(self):
        headings = [self.towards(n) for n in self.flockmates]
        x_component = statistics.mean([math.cos(math.radians(h)) for h in headings])
        y_component = statistics.mean([math.sin(math.radians(h)) for h in headings])
        return math.degrees(math.atan2(y_component, x_component))

    def towards(self, neighbor):
        dx = neighbor.point.x - self.point.x
        dy = neighbor.point.y - self.point.y
        return math.degrees(math.atan2(dy, dx))

    def turns_towards(self, other_heading, max_turn):
        angle = self.subtract_headings(other_heading, self.heading)
        self.turn_at_most(angle, max_turn)

    def turn_away(self, other_heading, max_turn):
        angle = self.subtract_headings(self.heading, other_heading)
        self.turn_at_most(angle, max_turn)

    def turn_at_most(self, angle, max_turn):
        if abs(angle) > max_turn:
            if angle > 0:
                self.turn(max_turn)
            else:
                self.turn(-1 * max_turn)
        else:
            self.turn(angle)

    def subtract_headings(self, h1, h2):
        diff = h1 - h2
        if -180 < diff < 180:
            angle = diff
        elif diff > 0:
            angle = diff - 360
        else:
            angle = diff + 360
        return angle

    def turn(self, angle):
        self.heading = (self.heading + angle) % 360


class FlockingSimulation(dworp.TwoStageSimulation):
    def __init__(self, params, observer):
        self.rng = np.random.RandomState(params.seed)
        self.area_width = params.area_size[0]
        self.area_height = params.area_size[1]
        env = dworp.NullEnvironment()
        time = dworp.BasicTime(params.steps)
        scheduler = dworp.BasicScheduler()
        self.space = Space2d(self.area_width, self.area_height)

        boids = [self.create_boid(params) for x in range(params.pop)]
        for boid in boids:
            self.space.add(boid, boid.point)

        super().__init__(boids, env, time, scheduler, observer)

    def create_boid(self, params):
        x = self.rng.uniform(0, self.area_width)
        y = self.rng.uniform(0, self.area_height)
        heading = self.rng.uniform(0, 360)
        return Boid(Point2d(x, y), heading, params, self.space)


class FlockingObserver(dworp.Observer):
    """Writes simulation state to stdout"""
    def step(self, time, agents, env):
        if time % 100 == 0:
            print("Step {}".format(time))


class PyGameRenderer(dworp.Observer):
    def __init__(self, size, fps, frames_in_anim):
        self.zoom = 5
        self.fps = fps
        self.width = size[0]
        self.height = size[1]

        pygame.init()
        pygame.display.set_caption("Flocking")
        self.screen = pygame.display.set_mode((self.zoom * self.width, self.zoom * self.height))
        self.background = pygame.Surface((self.screen.get_size()))
        self.background = self.background.convert()
        self.clock = pygame.time.Clock()
        self.filename_list = [os.path.join('temp' + str(n) + '.png')
                         for n in range(frames_in_anim)]
        self.frame = 0

    def start(self, now, agents, env):
        self.draw(agents)

    def step(self, now, agents, env):
        self.draw(agents)

    def stop(self, now, agents, env):
        pygame.quit()

    def draw(self, agents):
        radius = self.zoom // 2
        offset = radius
        self.background.fill((0, 0, 0))
        for agent in agents:
            x = round(self.zoom * agent.point.x + offset)
            y = round(self.zoom * agent.point.y + offset)
            pygame.draw.circle(self.background, (0, 255, 0), (x, y), radius)
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        self.clock.tick(self.fps)
        pygame.image.save(self.screen, self.filename_list[self.frame])
        self.frame = self.frame + 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)

    # parse command line
    parser = argparse.ArgumentParser()
    parser.add_argument("--pop", help="population (1-1000)", default=300, type=int)
    parser.add_argument("--vision", help="vision (0-10)", default=3.0, type=float)
    parser.add_argument("--min-separation", help="minimum separation (0-5)", default=1.0, type=float)
    parser.add_argument("--max-separate-turn", help="maximum turn to separate (0-20)", default=1.5, type=float)
    parser.add_argument("--max-align-turn", help="maximum turn to align (0-20)", default=5.0, type=float)
    parser.add_argument("--max-cohere-turn", help="maximum turn to cohere (0-20)", default=3.0, type=float)
    #parser.add_argument("--steps", help="number of steps in simulation", default=500, type=int)
    parser.add_argument("--steps", help="number of steps in simulation", default=100, type=int)
    parser.add_argument("--size", help="grid size formatted as XXXxYYY", default="100x100")
    parser.add_argument("--fps", help="frames per second", default="20", type=int)
    parser.add_argument("--seed", help="seed of RNG", default=42, type=int)
    args = parser.parse_args()

    # validate parameters of simulation
    assert(1 <= args.pop <= 1000)
    assert(0 <= args.vision <= 10)
    assert(0 <= args.min_separation <= 5)
    assert(0 <= args.max_separate_turn <= 20)
    assert(0 <= args.max_align_turn <= 20)
    assert(0 <= args.max_cohere_turn <= 20)
    args.area_size = [int(dim) for dim in args.size.split("x")]

    pgr = PyGameRenderer(args.area_size, args.fps, 100+1)

    observer = dworp.ChainedObserver(
        FlockingObserver(),
        pgr,
    )

    # create and run one realization of the simulation
    sim = FlockingSimulation(args, observer)
    sim.run()

    n_fps = args.fps
    outstring = 'flockingviz'

    filename_list = pgr.filename_list
    seconds_per_frame = 1.0 / n_fps
    frame_delay = str(int(seconds_per_frame * 100))
    command_list = ['convert', '-delay', frame_delay, '-loop', '0'] + filename_list + ['anim%s.gif' % (outstring)]
    gif_was_successful = False
    try:
        # Use the "convert" command (part of ImageMagick) to build the animation
        subprocess.call(command_list)
        gif_was_successful = True
    except:
        print("couldnt create the animation. Probably ImageMagick is not installed.")
        pass
    # Earlier, we saved an image file for each frame of the animation. Now
    # that the animation is assembled, we can (optionally) delete those files
    if gif_was_successful:
        for filename in filename_list:
            os.remove(filename)
