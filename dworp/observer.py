from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def step(self, index, agents, env):
        pass
