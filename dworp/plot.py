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


class VariablePlotter(Observer):  # pragma: no cover
    """Plot one or more variables from the Environment

    Args:
        var (string, list): Name or list of names of variable in Environment to plot
        fmt (string, list): Optional matplotlib format string or list of strings (default is "b")
        scrolling (int): Optional number of time steps in scroll or 0 for no scrolling
        title(string): Optional figure title (default is name of variable)
        xlabel(string): Optional x-axis label (default is "Time")
        ylabel(string): Optional y-axis label (default is name of variable)
        xlim(list): Optional starting x-axis limits as [xmin, xmax]
        ylim(list): Optional starting y-axis limits as [ymin, ymax]
        pause(float): Optional pause between updates (must be > 0)
    """
    def __init__(self, var, fmt="b", scrolling=0, title=None, xlabel="Time", ylabel=None,
                 xlim=None, ylim=None, pause=0.001):
        self.var_names = [var] if isinstance(var, str) else var
        self.fmt = self._prepare_format_option(fmt)
        self.scrolling = scrolling
        self.title = title if title else self._prepare_default_title()
        self.xlabel = xlabel
        self.ylabel = ylabel if ylabel else self._prepare_default_title()
        self.xlim = xlim
        self.ylim = ylim
        self.pause = pause
        self.fig = None
        self.axes_margin = 0.01

        self.time = []
        self.data = {name: [] for name in self.var_names}

    def _prepare_format_option(self, fmt):
        # fmt must be either same length as var_names or length 1
        format_ = [fmt] if isinstance(fmt, str) else fmt
        assert(len(format_) == 1 or len(format_) == len(self.var_names))
        if len(format_) != len(self.var_names):
            format_ = format_ * len(self.var_names)
        return dict(zip(self.var_names, format_))

    def _prepare_default_title(self):
        if len(self.var_names) == 0:
            return self.var_names[0]
        else:
            return ' & '.join(self.var_names)

    def start(self, now, agents, env):
        self.prepare()
        self.update(now, agents, env)

    def step(self, now, agents, env):
        self.update(now, agents, env)

    def stop(self, now, agents, env):
        plt.close(self.fig)

    def plot(self, now, agents, env):
        self.time.append(now)
        for name in self.var_names:
            self.data[name].append(getattr(env, name))
        if self.scrolling:
            plot_time = self.time[(-1 * self.scrolling):]
            plot_data = {name: data[(-1 * self.scrolling):] for name, data in self.data.items()}
        else:
            plot_time = self.time
            plot_data = self.data

        for name, data in plot_data.items():
            plt.plot(plot_time, data, self.fmt[name])
        axes = self.fig.axes[0]
        axes.set_xlabel(self.xlabel)
        axes.set_ylabel(self.ylabel)
        self.set_axes_limits(axes)

    def set_axes_limits(self, axes):
        if self.ylim:
            ylim = axes.get_ylim()
            margin = self.axes_margin * abs(ylim[1] - ylim[0])
            ymin = min(self.ylim[0], min(min(self.data.values())) - margin)
            ymax = max(self.ylim[1], max(max(self.data.values())) + margin)
            axes.set_ylim([ymin, ymax])
        if self.xlim:
            xmin = min(self.xlim[0], min(self.time))
            xmax = max(self.xlim[1], max(self.time))
            axes.set_xlim([xmin, xmax])

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
