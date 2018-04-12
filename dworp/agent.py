from abc import ABC, abstractmethod
import logging


class Agent(ABC):
    logger = logging.getLogger(__name__)

    def __init__(self, agent_id):
        self.agent_id = agent_id

    @abstractmethod
    def step(self, env):
        pass
