from dworp.plot import *
import unittest
import unittest.mock as mock
import matplotlib.pyplot as plt


class PlotPauseObserverTest(unittest.TestCase):
    def setUp(self):
        self.original_pause = plt.pause
        plt.pause = mock.Mock()

    def tearDown(self):
        plt.pause = self.original_pause

    def test_pause(self):
        obs = PlotPauseObserver(1)
        obs.step(0, [], None)
        self.assertTrue(plt.pause.called)
