# Copyright 2018, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the Modified BSD License.

from dworp.simulation import *
import unittest
import unittest.mock as mock
from dworp.scheduling import BasicScheduler
from dworp.time import Terminator, BasicTime


class FixedTerminator(Terminator):
    def __init__(self, num_steps):
        self.num_steps = num_steps
        self.count = 0

    def test(self, now, agents, env):
        self.count += 1
        return self.count == self.num_steps


class BasicSimulationTest(unittest.TestCase):
    def test_terminating(self):
        agents = [mock.Mock() for x in range(5)]
        env = mock.Mock()
        observer = mock.Mock()
        observer.step = mock.Mock()
        scheduler = BasicScheduler()
        time = BasicTime(5)
        terminator = FixedTerminator(2)
        sim = BasicSimulation(agents, env, time, scheduler, observer, terminator)

        sim.run()

        self.assertEqual(2, observer.step.call_count)
