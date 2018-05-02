from abc import ABC, abstractmethod
import itertools
import logging
import numpy as np


class IdentifierHelper:
    """Agent Identifier Generation Helper

    Create generators for identifiers.
    Example:
        gen = IdentifierHelper.get()
        agent_id = next(gen)
    """
    @classmethod
    def get(cls, start=1):
        """Get generator for numerical identifiers

        Args:
            start (int): optional starting identifier (default 1)

        Returns:
            generator
        """
        return itertools.count(start)


class Agent(ABC):
    """Base Agent class

    Args:
        agent_id (int, str): unique identifier for the agent
        size (int): length of the state vector

    Attributes:
        agent_id (int, str): unique identifier for the agent
        state (np.array): current state as vector of floats
        next_state (np.array): state at the end of time step
    """
    logger = logging.getLogger(__name__)

    def __init__(self, agent_id, size):
        self.agent_id = agent_id
        if size > 0:
            self.state = np.zeros(size, dtype='f')
            self.next_state = np.zeros(size, dtype='f')
        else:
            self.state = None
            self.next_state = None

    @abstractmethod
    def init(self, start_time, env):
        """Initialize the agent's state

        Args:
            start_time (int, float): Start time of the agent (usually the same as simulation)
            env (Environment): environment object (do not modify!)
        """
        pass

    @abstractmethod
    def step(self, new_time, env):
        """Update the agent's next state

        DO NOT MODIFY self.state in this method!

        Args:
            new_time (int, float): Current time of the simulation
            env (Environment): environment object (do not modify!)
        """
        pass

    def complete(self, new_time, env):
        """Complete a time step

        This copies the next state to current state.

        Args:
            new_time (int, float): Current time of the simulation
            env (Environment): environment object (do not modify!)
        """
        # Could replace with reference swap
        if self.state:
            np.copyto(self.state, self.next_state)
