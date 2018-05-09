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
import pickle as pkl
import time

# --- Constant Parameters ---

xdim = 10
ydim = 10
n_tsteps = 8000 # because we cycle through the 100 sites each time, this represents n_tsteps*100 events
features_list = [5,10,15]
numtraits_list = [5,10,15]
N = 20 # Number of trials to average over

printby = 1000
checkby = 100

logging.basicConfig(level=logging.WARN)

outfilename = "table2_sim_mean_output_N%d.txt" % (N)
outfilename_med = "table2_sim_med_output_N%d.txt" % (N)
outfilename_pkl = "table2_simout_N%d.pkl" % (N)

# --- Setting the Random Seed ---

#toplevelseed = 348675
toplevelseed = 8675
np.random.seed(toplevelseed)
seedlist = [np.random.randint(1,2**32 - 2) for _ in range(0,len(features_list)*len(numtraits_list)*N)]

# --- Run the Simulations ---

print("begin simulation")
start_time = time.clock()
allresults = np.zeros([len(features_list),len(numtraits_list),N])
alltimings = np.zeros([len(features_list),len(numtraits_list),N])
place = 0
g = igraph.Graph.Lattice([xdim,ydim], nei=1, directed=False, circular=False)
env = axelrod_aurora_test1.AxelrodEnvironment(g)
observer = axelrod_aurora_test1.AxelrodObserver(printby)
term = axelrod_aurora_test1.AxelrodTerminator(checkby)
for i in range(0,len(features_list)):
    num_features = features_list[i]
    for j in range(0,len(numtraits_list)):
        num_traits = numtraits_list[j]
        for k in range(0,N):
            this_s_time = time.clock()
            # get this simulation's seed
            curseed = seedlist[place]
            place = place + 1
            np.random.seed(curseed)
            timeobj = dworp.BasicTime(n_tsteps)
            # reset all the agent states
            agents = [axelrod_aurora_test1.Site(v,num_features,num_traits) for v in g.vs]
            # ensuring reproducibility by setting the seed
            scheduler = dworp.RandomOrderScheduler(np.random.RandomState(curseed+1))
            sim = dworp.TwoStageSimulation(agents, env, timeobj, scheduler, observer,terminator=term)
            sim.run()
            lastcount = observer.computenumregions(0,agents,env)
            allresults[i,j,k] = lastcount
            this_e_time = time.clock()
            alltimings[i,j,k] = this_e_time - this_s_time
try:
    end_time = time.clock()
    sim_time_minutes = float(end_time-start_time)/60.0
    print("simulation finished after %.2f minutes" % (sim_time_minutes))
except:
    print("error here")
    pdb.set_trace()

meanresults = np.zeros([len(features_list),len(numtraits_list)])
medianresults = np.zeros([len(features_list),len(numtraits_list)])
meantimingresults = np.zeros([len(features_list),len(numtraits_list)])
mediantimingresults = np.zeros([len(features_list),len(numtraits_list)])
for i in range(0,len(features_list)):
    for j in range(0,len(numtraits_list)):
        thislistresults = allresults[i,j,:]
        meanresults[i,j] = np.mean(thislistresults)
        medianresults[i,j] = np.median(thislistresults)
        thislistresultstime = alltimings[i,j,:]
        meantimingresults[i,j] = np.mean(thislistresultstime)
        mediantimingresults[i,j] = np.median(thislistresultstime)

# --- Save results to a pickle file ---

resultstuple = (allresults,meanresults,medianresults,xdim,ydim,n_tsteps,features_list,numtraits_list,N,
                toplevelseed,sim_time_minutes,alltimings,meantimingresults,mediantimingresults)
pkl.dump( resultstuple, open( outfilename_pkl, "wb" ) )

#partresultstuple = (allresults,xdim,ydim,n_tsteps,features_list,numtraits_list,N,toplevelseed,sim_time_minutes)
#pkl.dump( partresultstuple, open( "partial_"+outfilename_pkl, "wb" ) )


# --- Save results to text files ---
with open(outfilename,"w") as f:
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

with open(outfilename_med,"w") as f:
    f.write(" ")
    for i in range(0,len(numtraits_list)):
        f.write(",%d traits" % (numtraits_list[i]))
    f.write("\n")
    for i in range(0,len(features_list)):
        f.write("%d" % (features_list[i]))
        for j in range(0,len(numtraits_list)):
            f.write(",%.2f" % (medianresults[i,j]))
        f.write("\n")
    f.close()


print("done saving files")
