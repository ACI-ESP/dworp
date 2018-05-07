from dworp.time import *
import unittest


class BasicTimeTest(unittest.TestCase):
    def test_stopping(self):
        time = BasicTime(10)
        times = [x for x in time]
        self.assertEqual(10, len(times))
        self.assertEqual(1, times[0])
        self.assertEqual(10, times[-1])

    def test_start_time(self):
        time = BasicTime(5, 10)
        times = [x for x in time]
        self.assertEqual(5, len(times))
        self.assertEqual(11, times[0])
        self.assertEqual(15, times[-1])

    def test_floating_point_steps(self):
        time = BasicTime(5, step_size=0.5)
        times = [x for x in time]
        self.assertEqual(5, len(times))
        self.assertAlmostEqual(0.5, times[0])
        self.assertAlmostEqual(2.5, times[-1])


class InfiniteTimeTest(unittest.TestCase):
    def test_start_time(self):
        time = InfiniteTime(start=10)
        times = [next(time) for x in range(5)]
        self.assertEqual(11, times[0])
        self.assertEqual(15, times[-1])
