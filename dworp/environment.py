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
        self.state = np.zeros(size, dtype='f')

    @abstractmethod
    def init(self, start_time):
        """Initialize the environment's state

        Args:
            start_time (int, float): Start time of the environment
        """
        pass

    @abstractmethod
    def step(self, new_time, agents):
        """Update the environment's state

        Args:
            new_time (int, float): Current time of the simulation
            agents (list): list of Agent objects
        """
        pass


class GraphEnvironment(Environment):
    """Environment with a graph over the agents

    Attributes:
        state (np.array): environment state vector of floats
        graph (obj): graph object
    """
    def __init__(self, size, graph):
        super().__init__(size)
        self.graph = graph
