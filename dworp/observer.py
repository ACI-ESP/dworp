from abc import ABC, abstractmethod


class Observer(ABC):
    """Simulation observer

    Runs after each time step in the simulation.
    Can be used to collect data for analysis of the simulation.
    """
    @abstractmethod
    def step(self, index, agents, env):
        """Run the observer after a step of the simulation has finished

        Args:
            index (int): Zero-based time index
            agents (list): List of agents in the simulation
            env (object): Environment object for this time index
        """
        pass

    def done(self, index, agents, env):
        """Run the observer one last time when the simulation is complete

        Args:
            index (int): Zero-based time index
            agents (list): List of agents in the simulation
            env (object): Environment object for this time index
        """
        pass


class ChainedObserver(Observer):
    """Chain multiple observers into a sequence"""
    def __init__(self, *observers):
        """
        Args:
            *observers: Variable length arguments of Observer objects
        """
        self.observers = observers

    def step(self, index, agents, env):
        for observer in self.observers:
            observer.step(index, agents, env)

    def done(self, index, agents, env):
        for observer in self.observers:
            observer.done(index, agents, env)
