import logging


class Simulation:
    logger = logging.getLogger(__name__)

    def __init__(self, agents, env, time, scheduler, observer):
        self.agents = agents
        self.env = env
        self.time = time
        self.scheduler = scheduler
        self.observer = observer
        self.env.init(self.time.start_time)
        for agent in self.agents:
            agent.init(self.time.start_time, self.env)

    def run(self):
        for current_time in self.time:
            self.env.step(current_time, self.agents)
            schedule = self.scheduler.step(current_time, self.agents, self.env)
            for index in schedule:
                self.agents[index].step(current_time, self.env)
            self.observer.step(current_time, self.agents, self.env)
        self.observer.done(self.agents, self.env)
