import argparse
import collections
import dworp
import logging
import math
import matplotlib.pyplot as plt
import numpy as np


class Person(dworp.SelfNamingAgent):
    """Person that can have children"""
    def __init__(self, color, fertility, rng):
        super().__init__(0)
        self.color = color
        self.fertility = fertility
        self.rng = rng
        # minimum number of children per time step
        self.min_children = int(math.floor(fertility))
        # probability that an additional child is born
        self.additional_birth_probability = fertility - self.min_children

    def step(self, now, env):
        # reproduce and return children
        num_children = self.min_children
        if self.rng.uniform() < self.additional_birth_probability:
            num_children += 1
        return [Person(self.color, self.fertility, self.rng) for x in range(num_children)]


class BirthEnvironment(dworp.Environment):
    def __init__(self, colors):
        super().__init__(0)
        self.colors = colors
        self.data = collections.Counter()

    def step(self, now, agents):
        pass

    def complete(self, now, agents):
        self.data.clear()
        for agent in agents:
            self.data.update({agent.color: 1})


class BirthObserver(dworp.Observer):
    """Writes simulation state to stdout"""
    def start(self, time, agents, env):
        self.step(time, agents, env)

    def step(self, now, agents, env):
        print("Step {}: {} red\t{} blue".format(now, *self.get_counts(agents)))

    def stop(self, now, agents, env):
        print("Ending: only {} people left".format(agents[0].color))

    @staticmethod
    def get_counts(agents):
        num_red = sum([agent.color == "red" for agent in agents])
        num_blue = sum([agent.color == "blue" for agent in agents])
        return num_red, num_blue


class MatplotlibObservor(dworp.Observer):
    def __init__(self):
        self.time = []
        self.blue = []
        self.red = []

    def start(self, now, agents, env):
        plt.ion()
        plt.figure()
        plt.gcf().canvas.set_window_title("Populations")

    def step(self, now, agents, env):
        self.plot(now, agents, env)

    def plot(self, now, agents, env):
        plt.clf()

        self.time.append(now)
        self.blue.append(env.data['blue'])
        self.red.append(env.data['red'])

        plt.plot(self.time[-20:], self.blue[-20:], 'b')
        plt.plot(self.time[-20:], self.red[-20:], 'r')

        plt.xlabel("Generations")
        plt.ylabel("Population")

        axes = plt.gca()
        ylim = axes.get_ylim()
        margin = 0.01 * abs(ylim[1] - ylim[0])
        if len(self.time) < 20:
            axes.set_xlim([0, 20])
        ymin = min(300, min(self.red) - margin, min(self.blue) - margin)
        ymax = max(700, max(self.red) + margin, max(self.blue) + margin)
        axes.set_ylim([ymin, ymax])

        plt.draw_all()
        plt.pause(0.001)
        figures = plt.get_fignums()
        if not figures:
            quit()


class BirthTerminator(dworp.Terminator):
    """Stop when only one people color is left"""
    def test(self, now, agents, env):
        return 0 in BirthObserver.get_counts(agents)


class BirthParams:
    """Container for simulation parameters"""
    def __init__(self, capacity, red_fertility, blue_fertility, seed):
        self.capacity = capacity
        self.red_fertility = red_fertility
        self.blue_fertility = blue_fertility
        self.seed = seed


class BirthSimulation(dworp.BasicSimulation):
    """Birth and death simulation"""
    def __init__(self, params, observer):
        self.params = params
        self.rng = np.random.RandomState(params.seed)
        env = BirthEnvironment(['red', 'blue'])
        time = dworp.InfiniteTime()
        scheduler = dworp.BasicScheduler()
        terminator = BirthTerminator()

        # start out with an equal number of red and blue people
        num_people = params.capacity // 2
        red = [Person('red', params.red_fertility, self.rng) for x in range(num_people)]
        blue = [Person('blue', params.blue_fertility, self.rng) for x in range(num_people)]
        people = red + blue

        super().__init__(people, env, time, scheduler, observer, terminator)

    def run(self):
        self.observer.start(self.time.start_time, self.agents, self.env)
        current_time = 0
        for current_time in self.time:
            self.env.step(current_time, self.agents)
            schedule = self.scheduler.step(current_time, self.agents, self.env)
            # reproduce
            for index in schedule:
                new_people = self.agents[index].step(current_time, self.env)
                self.agents.extend(new_people)
            # death
            self.reap()
            self.env.complete(current_time, self.agents)
            self.observer.step(current_time, self.agents, self.env)
            if self.terminator.test(current_time, self.agents, self.env):
                break
        self.observer.stop(current_time, self.agents, self.env)

    def reap(self):
        """Kill people if in excess of carrying capacity"""
        num_people = len(self.agents)
        if num_people > self.params.capacity:
            probability = (num_people - self.params.capacity) / num_people
            self.logger.debug("Death probability: {}".format(probability))
            deaths = []
            for index, agent in enumerate(self.agents):
                if self.rng.uniform() < probability:
                    deaths.append(index)
            self.agents = [agent for index, agent in enumerate(self.agents) if index not in deaths]


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)

    # parse command line
    parser = argparse.ArgumentParser()
    parser.add_argument("--capacity", help="carrying capacity (1-4000)", default=1000, type=int)
    parser.add_argument("--red", help="red fertility (0-10)", default=2.0, type=float)
    parser.add_argument("--blue", help="blue fertility (0-10)", default=2.0, type=float)
    parser.add_argument("--seed", help="seed of RNG", default=42, type=int)
    args = parser.parse_args()

    # prepare parameters of simulation
    assert(1 <= args.capacity <= 4000)
    assert(0 <= args.red <= 10)
    assert(0 <= args.blue <= 10)
    params = BirthParams(args.capacity, args.red, args.blue, args.seed)

    # create and run one realization of the simulation
    observer = dworp.ChainedObserver(
        BirthObserver(),
        MatplotlibObservor()
    )
    sim = BirthSimulation(params, observer)
    sim.run()
