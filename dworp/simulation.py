import logging


class Simulation:
    logger = logging.getLogger(__name__)

    def __init__(self, agents, env, length, scheduler, observer=None):
        self.agents = agents
        self.env = env
        self.length = length
        self.scheduler = scheduler
        self.scheduler.set_agents(agents)
        self.observer = observer

    def run(self):
        index = 0
        for index in range(self.length):
            self.env.step()
            self.scheduler.step(index, self.env)
            if self.observer is not None:
                self.observer.step(index, self.agents, self.env)

        if self.observer is not None:
            self.observer.done(index, self.agents, self.env)
