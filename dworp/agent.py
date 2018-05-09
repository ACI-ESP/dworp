# Copyright 2018, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the Modified BSD License.

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
        state (np.array): public state vector
    """
    logger = logging.getLogger(__name__)

    def __init__(self, agent_id, size):
        self.agent_id = agent_id
        if size > 0:
            self.state = np.zeros(size, dtype='f')
        else:
            self.state = None

    def init(self, now, env):
        """Initialize the agent's state

        Use this if initialization requires access to data not available when the agent is constructed.
        For example, using environment data or birthing an agent later in simulation time line.
        You can add additional arguments in your implementation (when using your own Simulation class).

        Args:
            now (int, float): Start time of the agent (usually the same as simulation)
            env (Environment): environment object
        """
        pass

    @abstractmethod
    def step(self, now, env):
        """Update the agent's state

        The Environment is mutable and can be changed by the agent.
        You should think carefully about how agents change it due to update order/conflicts.

        Args:
            now (int, float): Current time of the simulation
            env (Environment): environment object
        """
        pass

    def complete(self, now, env):
        """Complete a time step

        Implement this if you need an agent to perform any operations at end of time step.

        Args:
            now (int, float): Current time of the simulation
            env (Environment): environment object
        """
        pass


class SelfNamingAgent(Agent):
    """Basic Agent with its identifier determined by agent count

    Args:
        size (int): length of the state vector

    Attributes:
        agent_id (int, str): unique identifier for the agent
        state (np.array): public state vector
    """
    count = 0

    def __init__(self, size):
        SelfNamingAgent.count += 1
        super().__init__(SelfNamingAgent.count, size)


class TwoStageAgent(Agent):
    """Agent that updates its public state vector after all agents do internal update.

    Use case: all agents update their future state based on their neighbors' current state.
    Then the future state is copied to their public state at the end of time step.
    This solves the problem of the order of agent updates mattering with respect to neighbors.

    Args:
        agent_id (int, str): unique identifier for the agent
        size (int): length of the state vector (must be > 0)

    Attributes:
        agent_id (int, str): unique identifier for the agent
        state (np.array): public state as vector
        next_state (np.array): state at the end of time step
    """
    def __init__(self, agent_id, size):
        assert(size > 0)
        super().__init__(agent_id, size)
        self.next_state = np.zeros(size, dtype='f')

    @abstractmethod
    def step(self, now, env):
        """Update the agent's next state

        Only change self.next_state in this method!
        Later self.next_state is copied to self.state in complete().

        Args:
            now (int, float): Current time of the simulation
            env (Environment): environment object
        """
        pass

    def complete(self, now, env):
        """Complete a time step

        This copies the next state to current state.

        Args:
            now (int, float): Current time of the simulation
            env (Environment): environment object
        """
        # Could replace with reference swap
        if self.state is not None:
            np.copyto(self.state, self.next_state)
