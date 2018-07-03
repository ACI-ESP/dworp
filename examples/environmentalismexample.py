"""
Aurora's version of the environmentalism example

July 3, 2018
"""
import dworp
import igraph
import logging
import numpy as np
import pdb


class Person(dworp.Agent):

    def __init__(self, vertex, numfeatures=16):
        super().__init__(vertex.index, numfeatures)
        vertex['agent'] = self
        self.vertex = vertex

    def step(self, now, env):
        neighbors = self.vertex.neighbors()
        logstring = ""
        if len(neighbors) > 0:
            selectedind = np.random.randint(0,len(neighbors))
            randfeatureind = np.random.randint(0,len(self.state))
            nvert = neighbors[selectedind]
            neighborstate = nvert["agent"].state
        else:
            logstring = "%sAgent %d has no neighbors!" % (logstring,self.agent_id)
        self.logger.info("%s" % (logstring))

    @property
    def cultural_state(self):
        logstring = ""
        for i in range(0,len(self.state)):
            logstring = "%s%d" % (logstring,int(self.state[i]))
        return logstring


class EEEnvironment(dworp.NetworkEnvironment):

    def __init__(self, network):
        super().__init__(1, network)

    def init(self, now):
        self.state.fill(0)

    def step(self, now, agents):
        self.logger.info("EEEnvironment did not need to update")


class EEObserver(dworp.Observer):
    def __init__(self, printby):
        self.printby = printby

    def step(self, now, agents, env):
        print("%d: current number of straw users is %d" % (now,self.computenumreusablestrawusers(self, now, agents, env)))
        pass

    def computenumreusablestrawusers(self, now, agents, env):
        count = 0
        for agent in agents:
            if agent.state[0] > 0:
                count = count + 1
        return count

    def complete(self, now, agents, env):
        print("Simulation over")


class EETerminator(dworp.Terminator):
    def __init__(self, printby):
        self.printby = printby

    def test(self, now, agents, env):
        # no more changes can happen when all neighboring Persons either no features in common or all features in common
        # make sure you only check this when current_time modulo printby == 0 (otherwise too much computation)
        if now % self.printby != 0:
            return False
        else:
            terminate = False
            if terminate:
                print("Terminating simulation early at time = {} because no neighboring agents can change".format(now))
            return terminate


class RegressionTest:
    def test(self):
        lastcountshouldbe = 4

        logging.basicConfig(level=logging.WARN)
        # ensuring reproducibility by setting the seed
        np.random.seed(5769)
        n_tsteps = 8000 # because we cycle through the 100 Persons each time, this represents 80K events
        n_agents = 1000
        g = igraph.Graph()

        mu = np.array([0.544, 0.504, 0.466, 0.482, 0.304])
        cov = np.zeros((5,5))
        cov[0,:] = [0.360000 ,0.066120,0.059520,0.093000,0.092040]
        cov[1,:] = [0.066120 ,0.336400,0.061132,0.061132,0.000000]
        cov[2,:] = [0.059520 ,0.061132,0.384400,0.042284,-0.021948]
        cov[3,:] = [0.093000 ,0.061132,0.042284,0.384400,0.098766]
        cov[4,:] = [0.092040 ,0.000000,-0.021948,0.098766,0.348100]
        personalities = np.random.multivariate_normal(mu,cov,n_agents)

        

        agents = [Person(v) for v in g.vs]
        env = EEEnvironment(g)
        time = dworp.BasicTime(n_tsteps)
        # ensuring reproducibility by setting the seed
        scheduler = dworp.RandomOrderScheduler(np.random.RandomState(4587))
        observer = EEObserver(1000)
        term = EETerminator(1000)
        sim = dworp.BasicSimulation(agents, env, time, scheduler, observer,terminator=term)

        sim.run()

        lastcount = observer.computenumreusablestrawusers(0,agents,env)
        print("Last Count = %d" % (lastcount))
        if lastcount == lastcountshouldbe:
            print("Regression test passed!")
            return True
        else:
            print("Regression test failed! last count should be %d" % (lastcountshouldbe))
            return False
