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
        def step(self, new_time, env):
            pass

    def test_creation_with_size(self):
        a = AgentTest.MockAgent("name", 5)
        self.assertEqual(5, a.state.shape[0])

    def test_creation_without_size(self):
        a = AgentTest.MockAgent("name", 0)
        self.assertIsNone(a.state)


class SelfNamingAgentTest(unittest.TestCase):
    class MockAgent(SelfNamingAgent):
        def step(self, new_time, env):
            pass

    def test_id(self):
        a1 = SelfNamingAgentTest.MockAgent(5)
        a2 = SelfNamingAgentTest.MockAgent(5)
        self.assertEqual(1, a1.agent_id)
        self.assertEqual(2, a2.agent_id)


class TwoStageAgentTest(unittest.TestCase):
    class MockAgent(TwoStageAgent):
        def step(self, new_time, env):
            self.next_state[1] = 42

    def test_state_switch_on_complete(self):
        agent = TwoStageAgentTest.MockAgent(agent_id=1, size=5)
        agent.step(0, None)
        agent.complete(0, None)
        self.assertEqual(0, agent.state[0])
        self.assertEqual(42, agent.state[1])
