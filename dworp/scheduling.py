# Copyright 2018, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the Modified BSD License.

from abc import ABC, abstractmethod
import itertools
import logging


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


class FastBernoulliScheduler(Scheduler):
    """Faster Bernoulli process scheduler

    This precomputes the schedule trading off memory for speed.
    The number of agents must be constant.

    Args:
        p (float): probability of heads (probability an agent updates)
        rng (numpy.random.RandomState): numpy random generator
        num_agents (int): constant number of agents in the simulation
        start (int): start time of the simulation (exclusive)
        stop (int): stop time of the simulation (exclusive)
    """
    SAMPLE_SIZE = 10000

    def __init__(self, p, rng, num_agents, start, stop):
        assert 0 <= p <= 1
        self.p = p
        self.rng = rng
        self.num_agents = num_agents
        self.t0 = start
        self.tN = stop
        self.schedule = self._create_schedule()

    def step(self, now, agents, env):
        try:
            return self.schedule[now]
        except KeyError:
            if now > self.tN:
                self.logger.warning("Simulation is continuing past end of schedule")
            return []

    def get_times(self):
        return sorted(self.schedule.keys())

    def _create_schedule(self):
        gen = self._get_wait_times(self.p, self.rng, self.SAMPLE_SIZE)
        times = []
        for i in range(self.num_agents):
            t = self.t0
            while True:
                t += next(gen)
                if t >= self.tN:
                    break
                times.append((i, t))

        # sort the times (takes n*log(n))
        times = sorted(times, key=lambda x: x[1])

        # create map from time to agents
        schedule = {}
        for k, v in itertools.groupby(times, lambda x: x[1]):
            schedule[k] = [x[0] for x in v]

        return schedule

    @staticmethod
    def _get_wait_times(p, rng, num_samples):
        samples = []
        while True:
            if not samples:
                samples = rng.geometric(p=p, size=num_samples).tolist()
            yield samples.pop()
