from dworp.scheduling import *
import unittest
import unittest.mock as mock


class RandomSampleSchedulerTest(unittest.TestCase):
    def test(self):
        scheduler = RandomSampleScheduler(50)
        schedule = scheduler.step(0, [mock.Mock()] * 100, None)
        self.assertEqual(50, len(schedule))
        self.assertEqual(50, len(set(schedule)))
