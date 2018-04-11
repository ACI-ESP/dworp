class Simulation:
    def __init__(self, agents, env, length, observer=None):
        self.agents = agents
        self.env = env
        self.length = length
        self.observer = observer

    def run(self):
        for i in range(self.length):
            self.env.step()
            for agent in self.agents:
                agent.step(self.env)
            if self.observer is not None:
                self.observer.step(i, self.agents, self.env)
