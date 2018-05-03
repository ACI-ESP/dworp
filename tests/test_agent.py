from dworp.agent import *
import unittest


class IdentifierHelperTest(unittest.TestCase):
    def test(self):
        # trivial test that serves as an example
        id_gen = IdentifierHelper.get(50)
        self.assertEqual(50, next(id_gen))
        self.assertEqual([51, 52, 53], [next(id_gen) for x in range(3)])


class AgentTest(unittest.TestCase):
    class MockAgent(Agent):
        def init(self, start_time, env):
            pass
        def step(self, new_time, env):
            self.next_state[1] = 42

    def test_state_switch_on_complete(self):
        agent = AgentTest.MockAgent(agent_id=1, size=5)
        agent.step(0, None)
        agent.complete(0, None)
        self.assertEqual(0, agent.state[0])
        self.assertEqual(42, agent.state[1])
