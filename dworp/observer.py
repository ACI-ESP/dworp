from abc import ABC, abstractmethod
import logging


class Observer(ABC):
    """Simulation observer

    Runs after each time step in the simulation.
    Can be used to collect data for analysis of the simulation.
    """
    logger = logging.getLogger(__name__)

    @abstractmethod
    def step(self, time, agents, env):
        """Run the observer after a step of the simulation has finished

        Args:
            time (int): Current time value
            agents (list): List of agents in the simulation
            env (object): Environment object for this time index
        """
        pass

    def done(self, agents, env):
        """Run the observer one last time when the simulation is complete

        Args:
            agents (list): List of agents in the simulation
            env (object): Environment object for this time index
        """
        pass


class ChainedObserver(Observer):
    """Chain multiple observers into a sequence

    Args:
        *observers: Variable length arguments of Observer objects
    """
    def __init__(self, *observers):
        self.observers = observers

    def step(self, time, agents, env):
        for observer in self.observers:
            observer.step(time, agents, env)

    def done(self, agents, env):
        for observer in self.observers:
            observer.done(agents, env)
