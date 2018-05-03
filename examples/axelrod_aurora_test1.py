__author__ = 'schmiac1'

"""
Aurora's Attempt to quickly implement Axelrod model of...

The Dissemination of Culture: A Model with Local Convergence and Global Polarization
Robert Axelrod
Journal of Conflict Resolution
Vol 41, Issue 2, pp. 203 - 226
April 1, 1997
http://journals.sagepub.com/doi/10.1177/0022002797041002001#articleCitationDownloadContainer

Time spent info.
May 1
Began reading paper cited above at 5:28pm
Based initial code on copy of the shorts.py example
Began editing code 5:35pm (using igraph Lattice for the graph)
6:25pm done with initial draft. Still need to modify the observer function so we can record outcomes
"""
import dworp
import igraph
import logging
import numpy as np


class Site(dworp.Agent):

    #cultural_features = np.zeros(5) # there are 5 cultural features that have integer values
    # the values of the cultural features are represented by the digits 0 through 9
    # these values are initialized uniformly at random for each site

    def __init__(self, vertex):
        super().__init__(vertex.index, 5)
        vertex['agent'] = self
        self.vertex = vertex

    def init(self, start_time, env):
        #self.state.fill(0)
        self.state[0] = float(np.random.randint(0,high=10))
        self.state[1] = float(np.random.randint(0,high=10))
        self.state[2] = float(np.random.randint(0,high=10))
        self.state[3] = float(np.random.randint(0,high=10))
        self.state[4] = float(np.random.randint(0,high=10))

    def step(self, new_time, env):
        neighbors = self.vertex.neighbors()
        logstring = ""
        if len(neighbors)>0:
            selectedind = np.random.randint(0,len(neighbors))
            randfeatureind = np.random.randint(0,len(self.state))
            neighborstate = neighbors[selectedind].state
            if (abs(self.state[randfeatureind]-neighborstate[randfeatureind]) < 0.001):
                # go ahead and interact
                # first compute G(s,n)
                indsdiffer = []
                for i in range(0,len(self.state)):
                    if (abs(self.state[i]-neighborstate[i]) > 0.001):
                        indsdiffer.append(i)
                if len(indsdiffer) > 0:
                    # G(s,n) is not empty so choose one of these features at random (to harmonize)
                    thischoice = np.random.randint(0,len(indsdiffer))
                    self.state[indsdiffer[thischoice]] = neighborstate[indsdiffer[thischoice]]
                    logstring = "%sAgent %d changed trait %d to value %d like neighbor %d" % (logstring,self.agent_id,indsdiffer[thischoice],int(neighborstate[indsdiffer[thischoice]]),neighbors[selectedind].agent_id)
                else:
                    logstring = "%sAgent %d had no differing traits from neighbor %d" % (logstring,self.agent_id,neighbors[selectedind].agent_id)
            else:
                logstring = "%sAgent %d chose not to interact with neighbor %d" % (logstring,self.agent_id,neighbors[selectedind].agent_id)
        else:
            logstring = "%sAgent %d has no neighbors!" % (logstring,self.agent_id)
        self.logger.info("%s" % (logstring))

    @property
    def cultural_state(self):
        logstring = ""
        for i in range(0,len(self.state)):
            logstring = "%s%d" % (logstring,int(self.state[i]))
        return logstring


class AxelrodEnvironment(dworp.NetworkEnvironment):

    def __init__(self, graph):
        super().__init__(1, graph)

    def init(self, start_time):
        self.state.fill(0)

    def step(self, new_time, agents):
        #self.state[self.TEMP] = np.random.randint(self.MIN_TEMP, self.MAX_TEMP)
        self.logger.info("AxelrodEnvironment did not need to update")


# A cultural region is defined as a set of contiguous sites with identical cultural features
class AxelrodObserver(dworp.Observer):
    def step(self, time, agents, env):
        count = sum([agent.wearing_shorts for agent in agents])
        print("{}: Temp {} - Shorts {}".format(time, env.temp, count))

    def done(self, agents, env):
        print("Simulation over")


logging.basicConfig(level=logging.WARN)
np.random.seed(34756)
xdim = 10
ydim = 10
n_tsteps = 800 # because we cycle through the 100 sites each time, this represents 80K events
g = igraph.Graph.Lattice([xdim,ydim], nei=1, directed=False, circular=False)
agents = [Site(v) for v in g.vs]
env = AxelrodEnvironment(g)
time = dworp.BasicTime(n_tsteps)
scheduler = dworp.RandomOrderScheduler(np.random.RandomState())
observer = AxelrodObserver()
sim = dworp.DoubleStageSimulation(agents, env, time, scheduler, observer)

sim.run()
