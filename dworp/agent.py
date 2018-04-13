from abc import ABC, abstractmethod
import logging
import numpy as np


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
        self.state = np.zeros(size, dtype='f')
        self.next_state = np.zeros(size, dtype='f')

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

    def complete(self):
        """Complete a time step by copying the next state to current state"""
        # Could replace with reference swap
        np.copyto(self.state, self.next_state)
