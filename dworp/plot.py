import matplotlib.pyplot as plt
from .observer import PauseObserver

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

    def start(self, current_time, agents, env):
        if self.start_flag:
            self.pause()

    def step(self, time, agents, env):
        self.pause()

    def done(self, agents, env):
        if self.stop_flag:
            self.pause()

    def pause(self):
        plt.pause(self.delay)
