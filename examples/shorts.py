"""
Whether you wear shorts depends on the temperature and whether your friends are wearing shorts
"""
import dworp
import igraph
import random


class ShortsAgent(dworp.Agent):
    def __init__(self, vertex):
        super().__init__(vertex.index)
        self.vertex = vertex
        vertex['agent'] = self
        self.wearing_shorts = False

    def step(self, env):
        num_neighbors = len(self.vertex.neighbors())
        count = sum([v['agent'].wearing_shorts for v in self.vertex.neighbors()])
        probability = 0.5 * env.temperature / float(30) + 0.5 * count / (float(num_neighbors) + 0.0001)
        self.wearing_shorts = random.random() < probability


class ShortsEnvironment(dworp.Environment):
    def __init__(self):
        self.temperature = 0

    def step(self):
        self.temperature = random.randint(0, 30)


class ShortsObserver(dworp.Observer):
    def step(self, index, agents, env):
        count = sum([agent.wearing_shorts for agent in agents])
        print("{}: Temp {} - Shorts {}".format(index, env.temperature, count))


g = igraph.Graph.Erdos_Renyi(n=100, p=0.05, directed=False)
agents = [ShortsAgent(v) for v in g.vs]
env = ShortsEnvironment()
observer = ShortsObserver()
scheduler = dworp.RandomOrderScheduler()
sim = dworp.Simulation(agents, env, 10, scheduler, observer)

sim.run()
