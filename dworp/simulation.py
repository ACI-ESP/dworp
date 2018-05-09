# Copyright 2018, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the Modified BSD License.

from abc import ABC, abstractmethod
import logging
from .time import NullTerminator


class Simulation(ABC):
    """Base Simulation class"""
    logger = logging.getLogger(__name__)

    @abstractmethod
    def run(self):
        """Run single realization of the simulation"""
        pass


class BasicSimulation(Simulation):
    """Simulation master

    Runs a single realization of the simulation.
    This will initialize the agents and the environment.

    Args:
        agents (list): list of initial agents
        env (Environment): environment object
        time (Time): time generation object
        scheduler (Scheduler): schedule generation object
        observer (Observer): records and logs data from the simulation
        terminator (Terminator): Optional simulation terminator
        two_stage (bool): Whether to perform a 2 stage update for agents
    """

    def __init__(self, agents, env, time, scheduler, observer, terminator=None, two_stage=False):
        self.agents = agents
        self.env = env
        self.time = time
        self.scheduler = scheduler
        self.observer = observer
        self.terminator = terminator if terminator else NullTerminator()
        self.two_stage = two_stage

        self.env.init(self.time.start_time)
        for agent in self.agents:
            agent.init(self.time.start_time, self.env)

    def run(self):
        """Run the realization to completion"""
        self.observer.start(self.time.start_time, self.agents, self.env)
        current_time = 0
        for current_time in self.time:
            self.env.step(current_time, self.agents)
            schedule = self.scheduler.step(current_time, self.agents, self.env)
            if self.two_stage:
                self._update_agents_two_stage(current_time, schedule)
            else:
                self._update_agents_one_stage(current_time, schedule)
            self.env.complete(current_time, self.agents)
            self.observer.step(current_time, self.agents, self.env)
            if self.terminator.test(current_time, self.agents, self.env):
                break
        self.observer.stop(current_time, self.agents, self.env)

    def _update_agents_one_stage(self, current_time, schedule):
        for index in schedule:
            self.agents[index].step(current_time, self.env)

    def _update_agents_two_stage(self, current_time, schedule):
        # this caches the schedule and reruns it for 2nd stage
        updated_agents = []
        for index in schedule:
            self.agents[index].step(current_time, self.env)
            updated_agents.append(index)
        # agents copy state to complete time step or perform final step calculations
        for index in updated_agents:
            self.agents[index].complete(current_time, self.env)


class TwoStageSimulation(BasicSimulation):
    """Simulation master

    Runs a single realization of the simulation.
    Each update has two stages for the agents.

    Args:
        agents (list): list of initial agents
        env (Environment): environment object
        time (Time): time generation object
        scheduler (Scheduler): schedule generation object
        observer (Observer): records and logs data from the simulation
        terminator (Terminator): Optional simulation terminator
    """
    logger = logging.getLogger(__name__)

    def __init__(self, agents, env, time, scheduler, observer, terminator=None):
        super().__init__(agents, env, time, scheduler, observer, terminator, True)
