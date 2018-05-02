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


class NetworkEnvironment(Environment):
    """Environment with a network over the agents

    Attributes:
        state (np.array): environment state vector of floats
        network (obj): network object
    """
    def __init__(self, size, network):
        super().__init__(size)
        self.network = network


class Grid:
    """Two dimension grid that agents live on

    Only one agent per grid location.
    Zero-based indexing.

    Args:
        width (int): width of the grid (x dimension)
        height (int): height of the grid (y dimension)
    """
    def __init__(self, width, height):
        self.width = height
        self.height = height
        self.data = np.empty(shape=(width, height), dtype=object)

    def occupied(self, x, y):
        """Does anyone live here"""
        return self.data[x, y] is not None

    def set(self, agent, x, y):
        """Place an agent here
        Does not check if anyone else lives here first!
        """
        self.data[x, y] = agent

    def get(self, x, y):
        """Get the current agent that lives here (or None)"""
        return self.data[x, y]

    def remove(self, x, y):
        """Remove the agent from here"""
        self.data[x, y] = None

    def move(self, agent, x1, y1, x2, y2):
        """Move an agent from location 1 to location 2
        Does not check if the agent actually lives at location 1!
        Does not check if anyone lives at location 2!
        """
        self.remove(x1, y1)
        self.set(agent, x2, y2)

    def neighbors(self, x, y):
        """Get the neighbor agents of this location

        Returns:
            list of agents
        """
        neighbors = []
        positions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for position in positions:
            x1 = x + position[0]
            y1 = y + position[1]
            if 0 <= x1 < self.width and 0 <= y1 < self.height and self.occupied(x1, y1):
                neighbors.append(self.data[x1, y1])
        return neighbors
