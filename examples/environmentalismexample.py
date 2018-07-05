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

    def __init__(self, vertex, numfeatures,traits):
        super().__init__(vertex.index, numfeatures+1) # the last state remembers if we adopted RS in the past
        vertex['agent'] = self
        self.vertex = vertex
        self.state[0:-1] = traits
        self.rs_i = 0 # changes
        self.eo_i = 1 # changes
        self.ea_i = 2 # changes
        self.o_i = 3
        self.c_i = 4
        self.e_i = 5
        self.a_i = 6
        self.n_i = 7
        self.w_i = 8
        self.lat_i = 9
        self.lon_i = 10
        self.g_i = 11
        self.ed_i = 12
        self.cd_i = 13
        self.past_i = 14
        self.state[self.past_i] = 0 # we start of not having adopted in the past

        # These ceiling and floor parameters are constant, so we'll compute them once here
        self.sa = self.state[self.e_i]**4
        self.rf = self.state[self.a_i]**2
        self.eof = min( 0.1 * (float(self.state[self.w_i])/600000 + 4*self.sa + self.state[self.o_i]),1)
        self.eac = 0.25 * (float(self.state[self.a_i]) + self.state[self.c_i] + 2.0*self.rf)

    def step(self, now, env):
        # In this function we update EO, EA, and then RS

        # we will need to look up the social activity levels (SA) of our neighbors as well as their
        # eating out tendency (EO) and environmental awarenesses (EA)
        neighbors = self.vertex.neighbors()
        sa_array = np.zeros((len(neighbors)))
        eo_array = np.zeros((len(neighbors)))
        ea_array = np.zeros((len(neighbors)))
        sum_for_EO = 0.0
        sum_for_EA = 0.0
        sum_for_denom = 0.0
        for i in range(0,len(neighbors)):
            nvert = neighbors[i]
            sa_array[i] = nvert["agent"].sa
            eo_array[i] = nvert["agent"].state[self.eo_i]
            ea_array[i] = nvert["agent"].state[self.ea_i]
            sum_for_EO = sum_for_EO + (sa_array[i] * eo_array[i])
            sum_for_EA = sum_for_EA + (sa_array[i] * ea_array[i])
            sum_for_denom = sum_for_denom + (sa_array[i])

        # update EO
        myEO = 1.0/(1.0 + (1.0 + self.rf)*sum_for_denom) * ( self.state[self.eo_i] + (1.0 + self.rf)*sum_for_EO )
        myEO = min(myEO,self.eof)
        self.state[self.eo_i] = myEO

        # update EA
        myEA = 1.0 / (1.0 + (1.0 + self.rf) * sum_for_denom) * (self.state[self.ea_i] + (1.0 + self.rf) * sum_for_EA)
        myEA = max(myEA, self.eac)
        self.state[self.ea_i] = myEA

        # update RS
        if self.state[self.rs_i] == 1: # we are using a RS right now
            # check if we want to discontinue
            cursum = self.rf + self.state[self.ea_i]
            if cursum <= 1:
                curprob = self.state[self.cd_i] * self.state[self.eo_i] * ( 1 - self.state[self.c_i] )/1.5
                thistrial = np.random.random()
                if thistrial < curprob:
                    # stop using the RS
                    self.state[self.rs_i] = 0
        else: # we are not currently using RS
            if self.state[self.past_i] == 1: # we used it in the past
                curval = self.state[self.cd_i] * self.state[self.eo_i] * (1 - self.state[self.c_i]) / 1.5
                if curval <= 0.5:
                    curprob = self.state[self.cd_i] * self.state[self.eo_i] * (self.rf + self.sa + self.state[self.ea_i]) / 3.0
                    thistrial = np.random.random()
                    if thistrial < curprob:
                        # start using the RS again
                        self.state[self.rs_i] = 1
            else: # we have never used it in the past
                if self.state[self.w_i] >= 150000:
                    threshval = (0.65 + (1-self.state[self.o_i]))/2
                    curval = self.state[self.cd_i] * self.state[self.eo_i] * (self.rf + self.sa + self.state[self.ea_i]) / 3.0
                    if curval >= threshval:
                        curprob = self.state[self.cd_i] * self.state[self.eo_i] * (self.rf + self.sa + self.state[self.ea_i]) / 3.0
                        thistrial = np.random.random()
                        if thistrial < curprob:
                            self.state[self.rs_i] = 1
                            self.state[self.past_i] = 1

        #logstring = ""
        #self.logger.info("%s" % (logstring))

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
        print("%d: current number of straw users is %d, number of adopters that no longer use is %d" %
              (now,self.computenumreusablestrawusers(now, agents, env),
               self.discontinuedreusableusers(now,agents,env)))
        pass

    def computenumreusablestrawusers(self, now, agents, env):
        count = 0
        for agent in agents:
            if agent.state[0] > 0:
                count = count + 1
        return count

    def discontinuedreusableusers(self, now, agents, env):
        count = 0
        for agent in agents:
            if agent.state[0] == 0:
                if agent.state[agent.past_i] == 1:
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
        n_tsteps = 8000
        n_agents = 1000
        n_friends = 20 # each agent has this many friends (based on the n_friends people who are geographically closest)

        mu = np.array([0.544, 0.504, 0.466, 0.482, 0.304])
        cov = np.zeros((5,5))
        cov[0,:] = [0.360000 ,0.066120,0.059520,0.093000,0.092040]
        cov[1,:] = [0.066120 ,0.336400,0.061132,0.061132,0.000000]
        cov[2,:] = [0.059520 ,0.061132,0.384400,0.042284,-0.021948]
        cov[3,:] = [0.093000 ,0.061132,0.042284,0.384400,0.098766]
        cov[4,:] = [0.092040 ,0.000000,-0.021948,0.098766,0.348100]
        personalities = np.random.multivariate_normal(mu,cov,n_agents)
        wealth = np.random.normal(300000,100000,n_agents)
        wealth[wealth > 600000] = 600000
        wealth[wealth < 10000]  = 10000
        offsets_lat = np.random.random((n_agents,1))
        offsets_lon = np.random.random((n_agents,1))
        lat = offsets_lat + 78.6569 # deg west
        lon = offsets_lon + 37.4316 # deg north
        gender = np.random.randint(0,1,(n_agents,1))
        education = np.random.randint(0,4,(n_agents,1))
        colddrinks = np.random.normal(0.80,0.15,n_agents)
        colddrinks[colddrinks > 1] = 1
        colddrinks[colddrinks < 0] = 0

        eatingout = np.random.normal(0.70,0.10,n_agents)
        eatingout[eatingout > 1] = 1
        eatingout[eatingout < 0] = 0
        envaware = np.random.random((n_agents,1))

        g = igraph.Graph()
        for i in range(0,n_agents):
            g.add_vertex(i)
        vs = g.vs
        agents = []
        for i in range(0,n_agents):
            traits = np.zeros((14))
            traits[0] = 0 # initially noone uses the reusable straw
            traits[1] = eatingout[i]
            traits[2] = envaware[i]
            traits[3:8] = personalities[i,:]
            traits[8] = wealth[i]
            traits[9] = lat[i]
            traits[10] = lon[i]
            traits[11] = gender[i]
            traits[12] = education[i]
            traits[13] = colddrinks[i]
            difflat = lat - lat[i]
            difflon = lon - lon[i]
            distsq = np.power(difflat,2) + np.power(difflon,2)
            sorted = np.argsort(distsq)
            friends = sorted[1:n_friends+1]
            for j in range(0,len(friends)):
                g.add_edge(i,int(friends[j]))
            curagent = Person(vs[i],14,traits)
            agents.append(curagent)

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


thistest = RegressionTest()
thistest.test()