__author__ = 'schmiac1'

"""
Aurora is using axelrod_aurora_test1 to reproduce Table 2 from the Axelrod paper.
"""
import sys
import dworp
import igraph
import logging
import numpy as np
import axelrod_aurora_test1
import pdb

# --- Constant Parameters ---

xdim = 10
ydim = 10
n_tsteps = 8000 # because we cycle through the 100 sites each time, this represents n_tsteps*100 events
features_list = [5,10,15]
numtraits_list = [5,10,15]
N = 100 # Number of trials to average over

printby = 1000
checkby = 1000

logging.basicConfig(level=logging.WARN)

outfilename = "table2_sim_output.csv"

# --- Setting the Random Seed ---

toplevelseed = 348675
np.random.seed(toplevelseed)
seedlist = [np.random.randint(1,2**32 - 2) for _ in range(0,len(features_list)*len(numtraits_list)*N)]

# --- Run the Simulations ---

allresults = np.zeros([len(features_list),len(numtraits_list),N])
place = 0
for i in range(0,len(features_list)):
    num_features = features_list[i]
    for j in range(0,len(numtraits_list)):
        num_traits = numtraits_list[j]
        for k in range(0,N):
            # get this simulation's seed
            curseed = seedlist[place]
            place = place + 1
            np.random.seed(curseed)
            g = igraph.Graph.Lattice([xdim,ydim], nei=1, directed=False, circular=False)
            agents = [axelrod_aurora_test1.Site(v) for v in g.vs]
            env = axelrod_aurora_test1.AxelrodEnvironment(g)
            time = dworp.BasicTime(n_tsteps)
            # ensuring reproducibility by setting the seed
            scheduler = dworp.RandomOrderScheduler(np.random.RandomState(curseed+1))
            observer = axelrod_aurora_test1.AxelrodObserver(printby)
            term = axelrod_aurora_test1.AxelrodTerminator(checkby)
            sim = dworp.TwoStageSimulation(agents, env, time, scheduler, observer,terminator=term)
            sim.run()
            lastcount = observer.computenumregions(0,agents,env)
            allresults[i,j,k] = lastcount

meanresults = np.zeros([len(features_list),len(numtraits_list),N])
medianresults = np.zeros([len(features_list),len(numtraits_list),N])
for i in range(0,len(features_list)):
    for j in range(0,len(numtraits_list)):
        thislistresults = allresults[i,j,:]
        meanresults[i,j] = np.mean(thislistresults)
        medianresults[i,j] = np.median(thislistresults)

with open(outfilename,"wb") as f:
    f.write(" ")
    for i in range(0,len(numtraits_list)):
        f.write(",%d traits" % (numtraits_list[i]))
    f.write("\n")
    for i in range(0,len(features_list)):
        f.write("%d" % (features_list[i]))
        for j in range(0,len(numtraits_list)):
            f.write(",%.2f" % (meanresults[i,j]))
        f.write("\n")
    f.close()

