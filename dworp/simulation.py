import logging


class Simulation:
    """Simulation master

    Runs a single realization of the simulation.
    This will initialize the agents and the environment.

    Args:
        agents (list): list of initial agents
        env (Environment): environment object
        time (Time): time generation object
        scheduler (Scheduler): schedule generation object
        observer (Observer): records and logs data from the simulation
    """
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
        """Run the realization to completion"""
        for current_time in self.time:
            self.env.step(current_time, self.agents)
            # agents update state
            schedule = self.scheduler.step(current_time, self.agents, self.env)
            for index in schedule:
                self.agents[index].step(current_time, self.env)
            # agents copy state to complete time step
            schedule = self.scheduler.step(current_time, self.agents, self.env)
            for index in schedule:
                self.agents[index].complete()
            self.observer.step(current_time, self.agents, self.env)
        self.observer.done(self.agents, self.env)
