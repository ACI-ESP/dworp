from dworp.environment import *
import unittest
import unittest.mock as mock


class GridTest(unittest.TestCase):
    def test_occupied(self):
        grid = Grid(10, 10)
        grid.set(mock.Mock(), 3, 2)

        self.assertTrue(grid.occupied(3, 2))
        self.assertFalse(grid.occupied(2, 3))

    def test_move(self):
        agent = mock.Mock()
        grid = Grid(10, 10)
        grid.set(agent, 3, 5)
        grid.move(3, 5, 8, 1)
        self.assertFalse(grid.occupied(3, 5))
        self.assertTrue(grid.occupied(8, 1))
        self.assertEqual(agent, grid.get(8, 1))

    def test_neighbors_edge_case(self):
        grid = Grid(10, 10)
        neighbors = [mock.Mock(), mock.Mock()]
        grid.set(neighbors[0], 0, 0)
        grid.set(neighbors[1], 1, 2)
        grid.set(mock.Mock(), 2, 1)

        n = grid.neighbors(0, 1)

        self.assertEqual(2, len(n))
        self.assertSetEqual(set(neighbors), set(n))
