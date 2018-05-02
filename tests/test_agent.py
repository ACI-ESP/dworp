from dworp.agent import *
import unittest


class IdentifierHelperTest(unittest.TestCase):
    def test(self):
        # trivial test that serves as an example
        id_gen = IdentifierHelper.get(50)
        self.assertEqual(50, next(id_gen))
        self.assertEqual([51, 52, 53], [next(id_gen) for x in range(3)])
