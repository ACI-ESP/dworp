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
May 3
5:46pm looking to fix the observer
7pm finished the observer, tested the printing of number of cultural regions, appears to work
"""
import dworp
import igraph
import logging
import numpy as np
import pdb


class Site(dworp.TwoStageAgent):

    #cultural_features = np.zeros(5) # there are 5 cultural features that have integer values
    # the values of the cultural features are represented by the digits 0 through 9
    # these values are initialized uniformly at random for each site

    def __init__(self, vertex, numfeatures=5, numtraitsper=10):
        super().__init__(vertex.index, numfeatures)
        vertex['agent'] = self
        self.vertex = vertex
        self.numtraits = numtraitsper

    def init(self, now, env):
        for i in range(0,len(self.state)):
            self.state[i] = float(np.random.randint(0,high=self.numtraits))

    # note to aurora: you need to modify next_state here!
    def step(self, now, env):
        # start by initializing next_state to the current state
        for i in range(0,len(self.state)):
            self.next_state[i] = self.state[i]

        neighbors = self.vertex.neighbors()
        logstring = ""
        if len(neighbors) > 0:
            selectedind = np.random.randint(0,len(neighbors))
            randfeatureind = np.random.randint(0,len(self.state))
            nvert = neighbors[selectedind]
            neighborstate = nvert["agent"].state
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
                    self.next_state[indsdiffer[thischoice]] = neighborstate[indsdiffer[thischoice]]
                    logstring = "%sAgent %d changed trait %d to value %d like neighbor %d" % (logstring,self.agent_id,indsdiffer[thischoice],int(neighborstate[indsdiffer[thischoice]]),nvert["agent"].agent_id)
                else:
                    logstring = "%sAgent %d had no differing traits from neighbor %d" % (logstring,self.agent_id,nvert["agent"].agent_id)
            else:
                logstring = "%sAgent %d chose not to interact with neighbor %d" % (logstring,self.agent_id,nvert["agent"].agent_id)
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

    def __init__(self, network):
        super().__init__(1, network)

    def init(self, now):
        self.state.fill(0)

    def step(self, now, agents):
        self.logger.info("AxelrodEnvironment did not need to update")



class AxelrodObserver(dworp.Observer):
    def __init__(self, printby):
        self.printby = printby

    def computenumregions(self, time, agents, env):
        # Method: we construct a dictionary whose keys are a features array and whose values are a list of lists of
        # contiguous agents. As we step through the entire list of agents, if that agent's features array is already in
        # the dict, then we check if is is a neighbor of any of the agents in lists. If it's a neighbor to more than one
        # list, then we merge the lists
        regiondict = dict()
        for i in range(0,len(agents)):
            curstate = tuple(agents[i].state.tolist())
            try:
                curval = regiondict[curstate]
                myneighbors = agents[i].vertex.neighbors()
                myneighborIDs = [a["agent"].agent_id for a in myneighbors]
                myNset = set(myneighborIDs)
                indsIamIn = []
                for k in range(0,len(curval)):
                    curlistagents = curval[k]
                    curlistagentIDs = [b.agent_id for b in curlistagents]
                    if not myNset.isdisjoint(curlistagentIDs):
                        indsIamIn.append(k)
                # we should have a list now of indices of sublists I am in
                if len(indsIamIn) > 1: # we need to merge
                    newlist = []
                    mergedlist = []
                    newlist.append(mergedlist)
                    place = 1
                    for k in range(0,len(curval)):
                        if k in indsIamIn:
                            mergedlist.extend(curval[k])
                        else:
                            #newlist[place] = curval[k]
                            newlist.append(curval[k])
                            place = place + 1
                    mergedlist.append(agents[i])
                    regiondict[curstate] = newlist
                elif len(indsIamIn) == 1: # just need to add to the right list
                    thislist = curval[indsIamIn[0]]
                    thislist.append(agents[i])
                else: # need to make a new list
                    newlist = []
                    newlist.append(agents[i])
                    curval.append(newlist)
            except KeyError:
                newlist = []
                componentlist = []
                componentlist.append(agents[i])
                newlist.append(componentlist)
                regiondict[curstate] = newlist
        # when done, the count is the same as the number of element lists in the vals of the regiondict
        count = 0
        for key in regiondict.keys():
            curval = regiondict[key]
            count = count + len(curval)
        return count

    def step(self, now, agents, env):
        # A cultural region is defined as a set of contiguous sites with identical cultural features
        # We need to count the cultural regions at desired time-steps
        #           (you may not want to do this expensive computation every time)
        if now % self.printby == 0:
            count = self.computenumregions(now, agents, env)
            print("{}: we have {} cultural regions".format(now, count))

    def complete(self, now, agents, env):
        print("Simulation over")


class AxelrodTerminator(dworp.Terminator):
    def __init__(self, printby):
        self.printby = printby

    def test(self, now, agents, env):
        # no more changes can happen when all neighboring sites either no features in common or all features in common
        # make sure you only check this when current_time modulo printby == 0 (otherwise too much computation)
        if now % self.printby != 0:
            return False
        else:
            found_pair_that_can_change = False
            for i in range(0,len(agents)):
                curstate = agents[i].state
                myneighbors = agents[i].vertex.neighbors()
                for j in range(0,len(myneighbors)):
                    curneivert = myneighbors[j]
                    neistate = curneivert["agent"].state
                    # are they all the same
                    #if not np.all(curstate == neistate) or np.all(curstate != neistate):
                    if not (np.sum(abs(curstate - neistate)) < 0.001 or np.all(abs(curstate - neistate) > 0.001)):
                        # if not (this pair has the same features) or (this pair shares no common features),
                        # => this pair must have some features that are the same, but not all
                        found_pair_that_can_change = True
                        #pdb.set_trace()
                        break
                if found_pair_that_can_change:
                    break
            terminate = not found_pair_that_can_change # dont terminate if you found change could happen
            if terminate:
                print("Terminating simulation early at time = {} because no neighboring agents can change".format(now))
            return terminate


if False:
    logging.basicConfig(level=logging.WARN)
    # ensuring reproducibility by setting the seed
    np.random.seed(34756)
    xdim = 10
    ydim = 10
    n_tsteps = 8000 # because we cycle through the 100 sites each time, this represents 80K events
    g = igraph.Graph.Lattice([xdim,ydim], nei=1, directed=False, circular=False)
    agents = [Site(v) for v in g.vs]
    env = AxelrodEnvironment(g)
    time = dworp.BasicTime(n_tsteps)
    # ensuring reproducibility by setting the seed
    scheduler = dworp.RandomOrderScheduler(np.random.RandomState(4587))
    observer = AxelrodObserver(1000)
    term = AxelrodTerminator(1000)
    sim = dworp.TwoStageSimulation(agents, env, time, scheduler, observer,terminator=term)

    sim.run()

    lastcount = observer.computenumregions(0,agents,env)
    print("Last Count = %d" % (lastcount))