"""
Whether you wear shorts depends on the temperature and whether your friends are wearing shorts
"""
import dworp
import igraph
import logging
import numpy as np


class CollegeStudent(dworp.Agent):
    SHORTS = 0

    def __init__(self, vertex):
        super().__init__(vertex.index, 1)
        vertex['agent'] = self
        self.vertex = vertex

    def init(self, start_time, env):
        self.state.fill(0)

    def step(self, new_time, env):
        neighbors = self.vertex.neighbors()
        count = sum([v['agent'].wearing_shorts for v in neighbors])
        probability = 0.6 * env.temp / float(env.MAX_TEMP) + 0.4 * count / float(len(neighbors) + 0.00001)
        self.next_state[self.SHORTS] = np.random.uniform() < probability
        self.logger.info("Agent {} has shorts status {}".format(self.agent_id, self.next_state[self.SHORTS]))

    @property
    def wearing_shorts(self):
        return bool(self.state[self.SHORTS])


class WeatherEnvironment(dworp.NetworkEnvironment):
    TEMP = 0
    MIN_TEMP = 0
    MAX_TEMP = 30

    def __init__(self, graph):
        super().__init__(1, graph)

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
g = igraph.Graph.Erdos_Renyi(n=100, p=0.05, directed=False)
agents = [CollegeStudent(v) for v in g.vs]
env = WeatherEnvironment(g)
time = dworp.BasicTime(10)
scheduler = dworp.BasicScheduler()
observer = ShortsObserver()
sim = dworp.TwoStageSimulation(agents, env, time, scheduler, observer)

sim.run()
