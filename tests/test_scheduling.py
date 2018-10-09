# Copyright 2018, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the Modified BSD License.

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


class BernoulliSchedulerTest(unittest.TestCase):
    def test_with_bad_probability(self):
        with self.assertRaises(AssertionError) as context:
            BernoulliScheduler(1.2, np.random.RandomState())

    def test_with_zero_agents(self):
        scheduler = BernoulliScheduler(.4, np.random.RandomState())
        self.assertEqual([], scheduler.step(1, [], None))

    def test_arrival_time_distribution(self):
        # calculate the mean of the wait time and verify it is approximately
        # equal to the expected value of the geometric distribution
        p = 0.4
        scheduler = BernoulliScheduler(p, np.random.RandomState())
        wait_times = []
        current_wait = 0
        while len(wait_times) < 10000:
            current_wait += 1
            if scheduler.step(0, ['mock agent'], None):
                wait_times.append(current_wait)
                current_wait = 0

        self.assertTrue(abs(1/p - np.mean(wait_times)) < 0.1)
