from abc import ABC, abstractmethod
import logging
import numpy as np


class Agent(ABC):
    logger = logging.getLogger(__name__)

    def __init__(self, agent_id, size):
        self.agent_id = agent_id
        self.state = np.zeros(size, dtype='f')

    @abstractmethod
    def init(self, start_time, env):
        pass

    @abstractmethod
    def step(self, new_time, env):
        pass
