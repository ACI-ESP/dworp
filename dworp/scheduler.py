from abc import ABC, abstractmethod
import logging
import numpy as np


class Scheduler(ABC):
    logger = logging.getLogger(__name__)

    def set_agents(self, agents):
        self.agents = agents

    @abstractmethod
    def step(self, index, env):
        pass


class BasicScheduler(Scheduler):
    def step(self, index, env):
        for agent in self.agents:
            agent.step(env)


class RandomOrderScheduler(Scheduler):
    def step(self, index, env):
        for i in np.random.permutation(len(self.agents)):
            self.agents[i].step(env)


class RandomSampleScheduler(Scheduler):
    def __init__(self, size):
        self.size = size

    def step(self, index, env):
        perm = np.random.permutation(len(self.agents))[:self.size]
        for i in perm:
            self.agents[i].step(env)
