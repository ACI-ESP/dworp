# Copyright 2018, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the Modified BSD License.

from abc import ABC, abstractmethod
import logging
import numpy as np


class Environment(ABC):
    """Environment for the simulation

    Args:
        size (int): length of the state vector

    Attributes:
        state (np.array): environment state vector of floats
    """
    logger = logging.getLogger(__name__)

    def __init__(self, size):
        if size > 0:
            self.state = np.zeros(size, dtype='f')
        else:
            self.state = None

    def init(self, now):
        """Initialize the environment's state

        Implement method for any initialization that requires knowledge of the start time.

        Args:
            now (int, float): Start time of the environment
        """
        pass

    @abstractmethod
    def step(self, now, agents):
        """Update the environment's state

        Args:
            now (int, float): Current time of the simulation
            agents (list): list of Agent objects
        """
        pass

    def complete(self, now, agents):
        """Complete a time step

        Implement this if you need to perform any operations at end of time step.

        Args:
            now (int, float): Current time of the simulation
            agents (list): list of Agent objects
        """
        pass


class NullEnvironment(Environment):
    """Empty environment"""
    def __init__(self):
        super().__init__(0)

    def step(self, now, agents):
        pass


class NetworkEnvironment(Environment):
    """Environment with a network over the agents

    Attributes:
        state (np.array): environment state vector of floats
        network (obj): network object
    """
    def __init__(self, size, network):
        super().__init__(size)
        self.network = network
