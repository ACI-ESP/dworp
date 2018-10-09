# Copyright 2018, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the Modified BSD License.

from abc import ABC, abstractmethod
import logging
from collections import OrderedDict
from itertools import groupby


class Scheduler(ABC):
    """Scheduling agents

    Determines which agents update for a particular time step.
    """
    logger = logging.getLogger(__name__)

    @abstractmethod
    def step(self, now, agents, env):
        """ Get the next step in schedule

        Args:
            now (int, float): current time of the simulation
            agents (list): list of Agent objects
            env (Environment): environment object

        Returns:
            list of agent indices or iterator over indices
        """
        pass


class BasicScheduler(Scheduler):
    """Schedules all agents in the order of the agents list"""
    def step(self, now, agents, env):
        return range(len(agents))


class RandomOrderScheduler(Scheduler):
    """Random permutation of all agents

    Args:
        rng (numpy.random.RandomState): numpy random generator
    """
    def __init__(self, rng):
        self.rng = rng

    def step(self, now, agents, env):
        return self.rng.permutation(len(agents))


class RandomSampleScheduler(Scheduler):
    """Uniformly sample from the list of agents

    Args:
        size (int): size of the sample (number of agents to update at each time step)
        rng (numpy.random.RandomState): numpy random generator
    """
    def __init__(self, size, rng):
        self.size = size
        self.rng = rng

    def step(self, now, agents, env):
        return self.rng.permutation(len(agents))[:self.size]


class BernoulliScheduler(Scheduler):
    """Schedules agents using a Bernoulli process

    Flips a coin at each time step to determine whether an agent updates.
    A Poisson process is a continuous-time version of a Bernoulli process.
    To obtain similar arrival time distributions to a discretized Poisson process,
    set p = e^-y where y is the rate of the Poisson process.

    Args:
        p (float): probability of heads (probability an agent updates)
        rng (numpy.random.RandomState): numpy random generator
    """
    def __init__(self, p, rng):
        assert 0 <= p <= 1
        self.p = p
        self.rng = rng

    def step(self, now, agents, env):
        trials = self.rng.binomial(n=1, p=self.p, size=len(agents))
        return [i for i, e in enumerate(trials) if e == 1]
