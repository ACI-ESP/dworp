# Copyright 2018, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the Modified BSD License.

from dworp.plot import *
import unittest
import unittest.mock as mock
import matplotlib
import matplotlib.pyplot as plt
import random
import time


class PlotPauseObserverTest(unittest.TestCase):
    # let developers filter the plotting tests
    plot = True

    def setUp(self):
        self.original_pause = plt.pause
        plt.pause = mock.Mock()

    def tearDown(self):
        plt.pause = self.original_pause

    def test_pause(self):
        obs = PlotPauseObserver(1)
        obs.step(0, [], None)
        self.assertTrue(plt.pause.called)


class VariablePlotterTest(unittest.TestCase):
    interactive = True

    @classmethod
    def setupClass(cls):
        print("Running interactive plotting tests")
        print("matplotlib.backend: {}".format(matplotlib.get_backend()))

    def confirm(self):
        result = input("Correct? ([y]/n): ") or "y"
        self.assertEqual("y", result)

    def test_with_default_arguments(self):
        plotter = VariablePlotter('data', title="Basic plot test")
        env = mock.Mock()
        agents = []

        env.data = 0
        plotter.start(0, agents, env)
        for x in range(1, 50):
            env.data = random.random()
            plotter.step(x, agents, env)
        time.sleep(1)
        plotter.stop(x, agents, env)

        self.confirm()

    def test_axes_limits(self):
        plotter = VariablePlotter('data', title="Limit test and format test", xlim=[0, 20], ylim=[0, 5], fmt="r--")
        env = mock.Mock()
        agents = []

        env.data = 0
        plotter.start(0, agents, env)
        for x in range(1, 50):
            env.data = 10 * random.random()
            plotter.step(x, agents, env)
        time.sleep(1)
        plotter.stop(x, agents, env)

        self.confirm()

    def test_scrolling(self):
        plotter = VariablePlotter('data', title="Scrolling test", scrolling=20, fmt='g')
        env = mock.Mock()
        agents = []

        env.data = 0
        plotter.start(0, agents, env)
        for x in range(1, 50):
            env.data = 10 * random.random()
            plotter.step(x, agents, env)
        time.sleep(1)
        plotter.stop(x, agents, env)

        self.confirm()
