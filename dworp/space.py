# Copyright 2018, The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
# Distributed under the terms of the Modified BSD License.

import logging
import numpy as np


class Grid:
    """Two dimension grid that agents live on

    Only one agent per grid location.
    Zero-based indexing.

    Args:
        width (int): width of the grid (x dimension)
        height (int): height of the grid (y dimension)
    """
    logger = logging.getLogger(__name__)

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = np.empty(shape=(width, height), dtype=object)

    def occupied(self, x, y):
        """Does anyone live here"""
        return self.data[x, y] is not None

    def add(self, agent, x, y):
        """Add an agent at the specified location
        Does not check if anyone else lives here first!
        """
        self.data[x, y] = agent

    def get(self, x, y):
        """Get the current agent that lives here (or None)"""
        return self.data[x, y]

    def remove(self, x, y):
        """Remove the agent from here"""
        self.data[x, y] = None

    def move(self, x1, y1, x2, y2):
        """Move an agent from location 1 to location 2
        Does not check if anyone lives at location 2!
        """
        agent = self.get(x1, y1)
        self.remove(x1, y1)
        self.data[x2, y2] = agent

    def neighbors(self, x, y):
        """Get the neighbor agents of this location

        Returns:
            list of agents
        """
        neighbors = []
        positions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for position in positions:
            x1 = x + position[0]
            y1 = y + position[1]
            if 0 <= x1 < self.width and 0 <= y1 < self.height and self.occupied(x1, y1):
                neighbors.append(self.data[x1, y1])
        return neighbors
