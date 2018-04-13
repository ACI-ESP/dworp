from dworp.observer import *
import unittest
import unittest.mock as mock


class ChainedObserverTest(unittest.TestCase):
    def test_step_called_for_all_observers(self):
        obs1 = mock.create_autospec(spec=Observer)
        obs2 = mock.create_autospec(spec=Observer)
        obs = ChainedObserver(obs1, obs2)

        obs.step(1, [], None)

        self.assertEqual([mock.call.step(1, [], None)], obs1.mock_calls)
        self.assertEqual([mock.call.step(1, [], None)], obs2.mock_calls)

    def test_done_called_for_all_observers(self):
        obs1 = mock.create_autospec(spec=Observer)
        obs2 = mock.create_autospec(spec=Observer)
        obs = ChainedObserver(obs1, obs2)

        obs.done([], None)

        self.assertEqual([mock.call.done([], None)], obs1.mock_calls)
        self.assertEqual([mock.call.done([], None)], obs2.mock_calls)
