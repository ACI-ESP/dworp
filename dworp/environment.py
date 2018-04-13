from abc import ABC, abstractmethod
import logging
import numpy as np


class Environment(ABC):
    logger = logging.getLogger(__name__)

    def __init__(self, size):
        self.state = np.zeros(size, dtype='f')

    @abstractmethod
    def init(self, start_time):
        pass

    @abstractmethod
    def step(self, new_time, agents):
        pass
