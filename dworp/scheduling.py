from abc import ABC, abstractmethod
from collections.abc import Iterator
import logging
import numpy as np


class Time(Iterator):
    @abstractmethod
    def get_start_time(self):
        pass


class BasicTime(Time):
    def __init__(self, num_steps, start=0, step_size=1):
        self.start_time = start
        self.time = start
        self.num_steps = num_steps
        self.step_size = step_size
        self.step_count = 0

    def get_start_time(self):
        return self.start_time

    def __next__(self):
        self.step_count += 1
        if self.step_count > self.num_steps:
            raise StopIteration
        self.time += self.step_size
        return self.time


class Scheduler(ABC):
    logger = logging.getLogger(__name__)

    @abstractmethod
    def step(self, time, agents, env):
        pass


class BasicScheduler(Scheduler):
    def step(self, time, agents, env):
        return range(len(agents))


class RandomOrderScheduler(Scheduler):
    def step(self, time, agents, env):
        return np.random.permutation(len(agents))


class RandomSampleScheduler(Scheduler):
    def __init__(self, size):
        self.size = size

    def step(self, time, agents, env):
        return np.random.permutation(len(agents))[:self.size]
