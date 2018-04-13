"""
Whether you wear shorts depends on the temperature and whether your friends are wearing shorts
"""
import dworp
import igraph
import logging
import numpy as np
import random


class CollegeStudent(dworp.Agent):
    SHORTS = 0

    def __init__(self, agent_id):
        super().__init__(agent_id, 1)

    def init(self, start_time, env):
        self.state.fill(0)

    def step(self, new_time, env):
        probability = env.temp / float(env.MAX_TEMP)
        self.state[self.SHORTS] = np.random.uniform() < probability
        self.logger.info("Agent {} has shorts status {}".format(self.agent_id, self.state[self.SHORTS]))

    @property
    def wearing_shorts(self):
        return bool(self.state[self.SHORTS])


class WeatherEnvironment(dworp.Environment):
    TEMP = 0
    MIN_TEMP = 0
    MAX_TEMP = 30

    def __init__(self):
        super().__init__(1)

    def init(self, start_time):
        self.state.fill(0)

    def step(self, new_time, agents):
        self.state[self.TEMP] = np.random.randint(self.MIN_TEMP, self.MAX_TEMP)
        self.logger.info("Temperature is now {}".format(self.state[self.TEMP]))

    @property
    def temp(self):
        return self.state[self.TEMP]


class ShortsObserver(dworp.Observer):
    def step(self, time, agents, env):
        count = sum([agent.wearing_shorts for agent in agents])
        print("{}: Temp {} - Shorts {}".format(time, env.temp, count))

    def done(self, agents, env):
        print("Simulation over")


logging.basicConfig(level=logging.WARN)
agents = [CollegeStudent(x) for x in range(100)]
env = WeatherEnvironment()
time = dworp.BasicTime(10)
scheduler = dworp.RandomOrderScheduler()
observer = ShortsObserver()
sim = dworp.Simulation(agents, env, time, scheduler, observer)

sim.run()
