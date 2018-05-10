# Copyright 2018, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the Modified BSD License.

from dworp.space import *
import unittest
import unittest.mock as mock


class GridTest(unittest.TestCase):
    def test_creation(self):
        grid = Grid(10, 20)
        self.assertEqual(None, grid.get(9, 19))
        self.assertRaises(IndexError, grid.get, 19, 9)

    def test_occupied(self):
        grid = Grid(10, 10)
        grid.add(mock.Mock(), 3, 2)

        self.assertTrue(grid.occupied(3, 2))
        self.assertFalse(grid.occupied(2, 3))

    def test_move(self):
        agent = mock.Mock()
        grid = Grid(10, 10)
        grid.add(agent, 3, 5)
        grid.move(3, 5, 8, 1)
        self.assertFalse(grid.occupied(3, 5))
        self.assertTrue(grid.occupied(8, 1))
        self.assertEqual(agent, grid.get(8, 1))

    def test_neighbors_edge_case(self):
        grid = Grid(10, 10)
        neighbors = [mock.Mock(), mock.Mock()]
        grid.add(neighbors[0], 0, 0)
        grid.add(neighbors[1], 1, 2)
        grid.add(mock.Mock(), 2, 1)

        n = grid.neighbors(0, 1)

        self.assertEqual(2, len(n))
        self.assertSetEqual(set(neighbors), set(n))
