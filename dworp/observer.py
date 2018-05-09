# Copyright 2018, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the Modified BSD License.

from abc import ABC, abstractmethod
import logging
import time


class Observer(ABC):
    """Simulation observer

    Runs after each time step in the simulation.
    Can be used to collect data for analysis of the simulation.
    """
    logger = logging.getLogger(__name__)

    def start(self, now, agents, env):
        """Run the observer after the simulation has been initialized

        Args:
            now (int, float): Start time of simulation
            agents (list): List of agents in the simulation
            env (object): Environment object for this time index
        """
        pass

    @abstractmethod
    def step(self, now, agents, env):
        """Run the observer after a step of the simulation has finished

        Args:
            now (int, float): Current time value
            agents (list): List of agents in the simulation
            env (object): Environment object for this time index
        """
        pass

    def stop(self, now, agents, env):
        """Run the observer one last time when the simulation has stopped

        Args:
            now (int, float): Current time value
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
        self.observers = list(observers)

    def append(self, observer):
        self.observers.append(observer)

    def start(self, now, agents, env):
        for observer in self.observers:
            observer.start(now, agents, env)

    def step(self, now, agents, env):
        for observer in self.observers:
            observer.step(now, agents, env)

    def stop(self, now, agents, env):
        for observer in self.observers:
            observer.stop(now, agents, env)


class KeyPauseObserver(Observer):
    """Requires a key press to get to the next time step

    Args:
        message (string): Optional message for the user
        start (bool): Optionally pause after initialization
        stop (bool): Optionally pause when simulation completes
    """
    def __init__(self, message="Press enter to continue...", start=False, stop=False):
        self.message = message
        self.start_flag = start
        self.stop_flag = stop

    def start(self, now, agents, env):
        if self.start_flag:
            input(self.message)

    def step(self, now, agents, env):
        input(self.message)

    def stop(self, now, agents, env):
        if self.stop_flag:
            input(self.message)


class PauseObserver(Observer):
    """Pause for x seconds between each time step

    This does not work with plotting during the simulation.
    Use dworp.plot.PlotPauseObserver instead.

    Args:
        delay (int): Length of delay in seconds
        start (bool): Optionally pause after initialization
        stop (bool): Optionally pause when simulation completes
    """
    def __init__(self, delay, start=False, stop=False):
        self.delay = delay
        self.start_flag = start
        self.stop_flag = stop

    def start(self, now, agents, env):
        if self.start_flag:
            self.pause()

    def step(self, now, agents, env):
        self.pause()

    def stop(self, now, agents, env):
        if self.stop_flag:
            self.pause()

    def pause(self):
        time.sleep(self.delay)


class PauseAtEndObserver(Observer):
    """Pause for x seconds at the end of the simulation

    This is useful if you want to keep a plot up on the screen.

    Args:
        delay (int): Length of delay in seconds
    """
    def __init__(self, delay):
        self.delay = delay

    def step(self, now, agents, env):
        pass

    def stop(self, now, agents, env):
        time.sleep(self.delay)
