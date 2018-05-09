# Copyright 2018, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the Modified BSD License.

from dworp.environment import *
import unittest


class EnvironmentTest(unittest.TestCase):
    class MockEnvironment(Environment):
        def step(self, now, agents):
            pass

    def test_creation_with_size(self):
        a = EnvironmentTest.MockEnvironment(5)
        self.assertEqual(5, a.state.shape[0])

    def test_creation_without_size(self):
        a = EnvironmentTest.MockEnvironment(0)
        self.assertIsNone(a.state)
