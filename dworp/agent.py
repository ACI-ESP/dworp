from abc import ABC, abstractmethod


class Agent(ABC):
    def __init__(self, agent_id):
        self.agent_id = agent_id

    @abstractmethod
    def step(self, env):
        pass
