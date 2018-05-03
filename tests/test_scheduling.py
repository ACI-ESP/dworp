from dworp.scheduling import *
import unittest
import unittest.mock as mock
import numpy as np


class RandomSampleSchedulerTest(unittest.TestCase):
    def test(self):
        scheduler = RandomSampleScheduler(50, np.random.RandomState())
        schedule = scheduler.step(0, [mock.Mock()] * 100, None)
        self.assertEqual(50, len(schedule))
        self.assertEqual(50, len(set(schedule)))
