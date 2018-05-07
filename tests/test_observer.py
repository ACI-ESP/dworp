from dworp.observer import *
import unittest
import unittest.mock as mock
import builtins
import time


class ChainedObserverTest(unittest.TestCase):
    def test_start_called_for_all_observers(self):
        obs1 = mock.create_autospec(spec=Observer)
        obs2 = mock.create_autospec(spec=Observer)
        obs = ChainedObserver(obs1, obs2)

        obs.start(0, [], None)

        self.assertEqual([mock.call.start(0, [], None)], obs1.mock_calls)
        self.assertEqual([mock.call.start(0, [], None)], obs2.mock_calls)

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


class KeyPauseObserverTest(unittest.TestCase):
    def setUp(self):
        self.original_input = builtins.input
        builtins.input = mock.Mock()

    def tearDown(self):
        builtins.input = self.original_input

    def test_start_flag_default(self):
        obs = KeyPauseObserver()
        obs.start(0, [], None)
        self.assertFalse(builtins.input.called)

    def test_start_flag_on(self):
        obs = KeyPauseObserver(start=True)
        obs.start(0, [], None)
        self.assertTrue(builtins.input.called)

    def test_stop_flag_default(self):
        obs = KeyPauseObserver()
        obs.done([], None)
        self.assertFalse(builtins.input.called)

    def test_stop_flag_on(self):
        obs = KeyPauseObserver(stop=True)
        obs.done([], None)
        self.assertTrue(builtins.input.called)


class PauseObserverTest(unittest.TestCase):
    def setUp(self):
        self.original_sleep = time.sleep
        time.sleep = mock.Mock()

    def tearDown(self):
        time.sleep = self.original_sleep

    def test_default_params(self):
        obs = PauseObserver(1)
        obs.step(0, [], None)
        self.assertTrue(time.sleep.called)

    def test_start_flag_default(self):
        obs = PauseObserver(1)
        obs.start(0, [], None)
        self.assertFalse(time.sleep.called)

    def test_start_flag_on(self):
        obs = PauseObserver(1, start=True)
        obs.start(0, [], None)
        self.assertTrue(time.sleep.called)

    def test_stop_flag_default(self):
        obs = PauseObserver(1)
        obs.done([], None)
        self.assertFalse(time.sleep.called)

    def test_stop_flag_on(self):
        obs = PauseObserver(1, stop=True)
        obs.done([], None)
        self.assertTrue(time.sleep.called)
