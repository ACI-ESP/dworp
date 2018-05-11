"""
Aurora is using testing scaling efficiency for axelrod_aurora_test1 (with num agents)
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

#square_dim_list = [10,20,40]
square_dim_list = [10,20,30]
numagents_list = [x**2 for x in square_dim_list]

n_tsteps = 8000 # because we cycle through the 100 sites each time, this represents n_tsteps*100 events
N = 3 #10 # Number of trials to average over

num_features = 5
num_traits = 10
    
printby = 1000
checkby = 1000

logging.basicConfig(level=logging.WARN)

outfilename = "scalingtest_mean_output_N%d.txt" % (N)
outfilename_med = "scalingtest_med_output_N%d.txt" % (N)
outfilename_pkl = "scalingtestout_N%d.pkl" % (N)

# --- Setting the Random Seed ---

#toplevelseed = 348675
toplevelseed = 8675
np.random.seed(toplevelseed)
seedlist = [np.random.randint(1,2**32 - 2) for _ in range(0,len(square_dim_list)*N)]

# --- Run the Simulations ---

print("begin simulation")
start_time = time.clock()
allresults = np.zeros([len(square_dim_list),N])
alltimings = np.zeros([len(square_dim_list),N])
place = 0
observer = axelrod_aurora_test1.AxelrodObserver(printby)
term = axelrod_aurora_test1.AxelrodTerminator(checkby)
for i in range(0,len(square_dim_list)):
    xdim = square_dim_list[i]
    ydim = square_dim_list[i]
    g = igraph.Graph.Lattice([xdim,ydim], nei=1, directed=False, circular=False)
    env = axelrod_aurora_test1.AxelrodEnvironment(g)
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
        allresults[i,k] = lastcount
        this_e_time = time.clock()
        alltimings[i,k] = this_e_time - this_s_time
try:
    end_time = time.clock()
    sim_time_minutes = float(end_time-start_time)/60.0
    print("simulation finished after %.2f minutes" % (sim_time_minutes))
except:
    print("error here")
    pdb.set_trace()

meanresults = np.zeros(len(square_dim_list))
medianresults = np.zeros(len(square_dim_list))
meantimingresults = np.zeros(len(square_dim_list))
mediantimingresults = np.zeros(len(square_dim_list))
for i in range(0,len(square_dim_list)):
    thislistresults = allresults[i,:]
    meanresults[i] = np.mean(thislistresults)
    medianresults[i] = np.median(thislistresults)
    thislistresultstime = alltimings[i,:]
    meantimingresults[i] = np.mean(thislistresultstime)
    mediantimingresults[i] = np.median(thislistresultstime)

# --- Save results to a pickle file ---

resultstuple = (allresults,meanresults,medianresults,num_features,num_traits,n_tsteps,square_dim_list,numagents_list,N,
                toplevelseed,sim_time_minutes,alltimings,meantimingresults,mediantimingresults)
pkl.dump( resultstuple, open( outfilename_pkl, "wb" ) )

#partresultstuple = (allresults,xdim,ydim,n_tsteps,square_dim_list,numtraits_list,N,toplevelseed,sim_time_minutes)
#pkl.dump( partresultstuple, open( "partial_"+outfilename_pkl, "wb" ) )


# --- Save results to text files ---
with open(outfilename,"w") as f:
    for i in range(0,len(square_dim_list)):
        f.write("%d" % (square_dim_list[i]))
        f.write(",%d" % (numagents_list[i]))
        f.write(",%.2f" % (meanresults[i]))
        f.write(",%.2f" % (meantimingresults[i]))
        f.write("\n")
    f.close()

with open(outfilename_med,"w") as f:
    for i in range(0,len(square_dim_list)):
        f.write("%d" % (square_dim_list[i]))
        f.write(",%d" % (numagents_list[i]))
        f.write(",%.2f" % (medianresults[i]))
        f.write(",%.2f" % (mediantimingresults[i]))
        f.write("\n")
    f.close()

print("done saving files")

