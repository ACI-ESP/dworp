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
        size (int): size of the sample
        rng (numpy.random.RandomState): numpy random generator
    """
    def __init__(self, size, rng):
        self.size = size
        self.rng = rng

    def step(self, now, agents, env):
        return self.rng.permutation(len(agents))[:self.size]

class PoissonScheduler(Scheduler):
    """
    Calculates update times for a set of users that will be chosen according to the model for Poisson arrivals.
    Each user will wake up at exponentially distributed random wait times, with a uniform parameter lambda, that
    is constant over time and constant across users. Times are all integer-valued (could be interpreted as seconds).

    Args:
        size (int): size of the sample (i.e., the number of actors/agents)
        rng (numpy.random.RandomState): numpy random generator
        t0: Overall period start time (we ensure nothing is scheduled for this time)
        tN: Overall period stop time (exclusive)
        lmda: Lambda parameter for the exponential samples
    """
    def __init__(self, size, rng, t0, tN, lmda):
        self.size = size
        self.rng = rng
        self.t0 = t0
        self.tN = tN
        self.lmda = lmda
        thisschedule = self.create_schedule(size, t0, tN, lmda)
        self.schedule_dict = thisschedule

    def step(self, now, agents, env):
        try:
            thistimeagentinds = self.schedule_dict[now]
        except KeyError:
            print("Error in PoissonScheduler, calling step with a time that is not in the schedule, %f" % (now))
            raise("Error in PoissonScheduler, calling step with a time that is not in the schedule")
        return thistimeagentinds

    def create_schedule(self, size, t0, tN, lmda):
        # note that the time_dict returned is an ordered dict with keys the integer-valued times
        # Loop through all users and generate login times from their start time to tN
        times = []
        for i in range(0,size):
            t = t0
            counter = 0
            while t < tN and counter < 1e4:
                counter = counter + 1
                new_increment = self.rng.exponential(scale=lmda)
                integer_increment = round(new_increment)
                if integer_increment > 0:
                    t = t + integer_increment
                    if t < tN:
                        times.append((i, t))

        # Sort the times (takes n*log(n))
        times = sorted(times, key=lambda x: x[1])

        # Since some users will have identical login times, group by time and create an OrderedDict by time with entries
        # containing a list of users logging in at that time
        time_dict = OrderedDict()
        for k, v in groupby(times, lambda x: x[1]):
            time_dict[k] = list([x[0] for x in v])

        return time_dict