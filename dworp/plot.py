# Copyright 2018, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the Modified BSD License.

import matplotlib.pyplot as plt
from .observer import Observer, PauseObserver

# Note: do not include this in __init__.py so that dworp does not have a hard requirement
# for matplotlib.


class PlotPauseObserver(PauseObserver):
    """Pause for x seconds between each time step

    This works when you are plotting between time steps.

    Args:
        delay (int): Length of delay in seconds
        start (bool): Optionally pause after initialization
        stop (bool): Optionally pause when simulation completes
    """
    def __init__(self, delay, start=False, stop=False):
        super().__init__(delay, start, stop)

    def pause(self):
        plt.pause(self.delay)


class VariablePlotter(Observer): # pragma: no cover
    """Plot one or more variables from the Environment"""
    def __init__(self, var, title=None, xlabel="Time", ylabel=None, pause=0.001):
        self.var_name = var
        self.title = title if title else var
        self.xlabel = xlabel
        self.ylabel = ylabel if ylabel else var
        self.pause = pause
        self.fig = None

        self.time = []
        self.data = []

    def start(self, now, agents, env):
        self.prepare()
        self.update(now, agents, env)

    def step(self, now, agents, env):
        self.update(now, agents, env)

    def stop(self, now, agents, env):
        plt.close(self.fig)

    def plot(self, now, agents, env):
        self.time.append(now)
        self.data.append(getattr(env, self.var_name))

        plt.plot(self.time, self.data, 'b')
        axis = self.fig.axes[0]
        axis.set_xlabel(self.xlabel)
        axis.set_ylabel(self.ylabel)

    def prepare(self):
        # turn interactive mode on and create an empty figure
        plt.ion()
        self.fig = plt.figure()
        self.fig.canvas.set_window_title(self.title)

    def update(self, now, agents, env):
        # clear figure, create new plot, and update figure
        plt.clf()
        self.plot(now, agents, env)
        plt.draw()
        # pause to give time for matplotlib to update figure
        plt.pause(self.pause)
        # if figure is closed, terminate
        figures = plt.get_fignums()
        if not figures:
            quit()
