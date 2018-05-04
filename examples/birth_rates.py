import argparse
import dworp
import logging
import math
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

    def step(self, new_time, env):
        # reproduce and return children
        num_children = self.min_children
        if self.rng.uniform() < self.additional_birth_probability:
            num_children += 1
        return [Person(self.color, self.fertility, self.rng) for x in range(num_children)]


class BirthObserver(dworp.Observer):
    """Writes simulation state to stdout"""
    def start(self, time, agents, env):
        print("Starting: {} red\t{} blue".format(*self.get_counts(agents)))

    def step(self, time, agents, env):
        print("Step {}: {} red\t{} blue".format(time, *self.get_counts(agents)))

    def done(self, agents, env):
        print("Ending: only {} people left".format(agents[0].color))

    @staticmethod
    def get_counts(agents):
        num_red = sum([agent.color == "red" for agent in agents])
        num_blue = sum([agent.color == "blue" for agent in agents])
        return num_red, num_blue


class BirthTerminator(dworp.Terminator):
    """Stop when only one people color is left"""
    def test(self, time, agents, env):
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
        env = dworp.NullEnvironment()
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
        for current_time in self.time:
            self.env.step(current_time, self.agents)
            schedule = self.scheduler.step(current_time, self.agents, self.env)
            # reproduce
            for index in schedule:
                new_people = self.agents[index].step(current_time, self.env)
                self.agents.extend(new_people)
            # death
            self.reap()
            self.observer.step(current_time, self.agents, self.env)
            if self.terminator.test(current_time, self.agents, self.env):
                break
        self.observer.done(self.agents, self.env)

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
    params = BirthParams(args.capacity, args.red, args. blue, args.seed)

    # create and run one realization of the simulation
    sim = BirthSimulation(params, BirthObserver())
    sim.run()
