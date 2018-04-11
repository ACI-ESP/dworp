from abc import ABC, abstractmethod


class Environment(ABC):

    @abstractmethod
    def step(self):
        pass
