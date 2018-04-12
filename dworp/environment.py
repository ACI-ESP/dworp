from abc import ABC, abstractmethod
import logging


class Environment(ABC):
    logger = logging.getLogger(__name__)

    @abstractmethod
    def step(self):
        pass
