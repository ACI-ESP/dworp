"""
Whether you wear shorts depends on the temperature and whether your friends are wearing shorts
"""
import os, sys
_root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, _root_dir)

import dworp
import igraph
import logging
import numpy as np
import random

class DiseaseAgent(dworp.TwoStageAgent):
    DISEASE_STATE = 0
    HEALTHY_CODE = 0
    INFECTED_CODE = 1
    DEAD_CODE = 2
    RECOVERED_CODE = 3
    DEATH_PROBABILITY = 0.03
    RECOVER_PROBABILITY = 0.05
    IMMUNITY_THRESHOLD_HEALTHY_NEIGHBORS = 7

    def __init__(self, width, x, y):
        super().__init__(x*width+y, 1)
        self.x = x
        self.y = y        
        #vertex['agent'] = self
        #self.vertex = vertex

    def init(self, now, env):
        self.state.fill(self.HEALTHY_CODE)
        
    def add_grid(self, grid):
        self.grid = grid

    def step(self, now, env):
        if self.healthy or self.recovered:
            #print("agent at x:{0}, y:{1}, healthy or recovered".format(self.x, self.y))            
            neighbors = self.grid.neighbors(self.x, self.y)
            count_healthy_neighbors = sum([v.healthy for v in neighbors])
            #print("num healthy neighbors: ", count_healthy_neighbors)
            if count_healthy_neighbors < self.IMMUNITY_THRESHOLD_HEALTHY_NEIGHBORS:                
                #print("too few healthy neighbors, checking for infection")
                count_infected_neighbors = sum([v.infected for v in neighbors])
                #print("num infected neighbors: ", count_infected_neighbors)
                probability_infection = count_infected_neighbors * 1.0 / float(len(neighbors))
                #print("probability infection: ", probability_infection)
                prob_check = np.random.uniform()
                #print("prob check: ", prob_check)
                if prob_check < probability_infection:
                    #print("infecting agent at x: ", self.x, " y: ", self.y)
                    self.infect()
        elif self.infected:
            if np.random.uniform() < self.RECOVER_PROBABILITY:
                self.recover()
            elif np.random.uniform() < self.DEATH_PROBABILITY:
                self.kill()
            
        self.logger.info("Agent {} has disease status {}".format(self.agent_id, self.next_state[self.DISEASE_STATE]))

    @property
    def infected(self):
        return bool(self.state[self.DISEASE_STATE] == self.INFECTED_CODE)

    @property
    def recovered(self):
        return bool(self.state[self.DISEASE_STATE] == self.RECOVERED_CODE)

    @property
    def healthy(self):
        return bool(self.state[self.DISEASE_STATE] == self.HEALTHY_CODE)
        
    @property
    def dead(self):
        return bool(self.state[self.DISEASE_STATE] == self.DEAD_CODE)
        
    def infect(self):
        self.next_state[self.DISEASE_STATE] = self.INFECTED_CODE
        
    def kill(self):
        self.next_state[self.DISEASE_STATE] = self.DEAD_CODE
        
    def recover(self):
        self.next_state[self.DISEASE_STATE] = self.RECOVERED_CODE


class WeatherEnvironment(dworp.NetworkEnvironment):    

    def __init__(self, graph):
        super().__init__(1, graph)

    def init(self, now):
        self.state.fill(0)

    def step(self, now, agents):
        pass

    @property
    def temp(self):
        pass

class DiseaseObserver(dworp.Observer):
    def step(self, now, agents, env):
        count_healthy = sum([agent.healthy for agent in agents])*100.0/len(agents)
        count_infected = sum([agent.infected for agent in agents])*100.0/len(agents)
        count_dead = sum([agent.dead for agent in agents])*100.0/len(agents)
        count_recovered = sum([agent.recovered for agent in agents])*100.0/len(agents)
        #print("{}: Healthy {} - Infected {} - Dead {} - Recovered {}".format(now, count_healthy, count_infected, \
        #      count_dead, count_recovered))
        print("{},{},{},{},{}".format(now,count_healthy,count_infected,count_dead,count_recovered))

    def stop(self, now, agents, env):
        print("Simulation over")


logging.basicConfig(level=logging.WARN)
#g = igraph.Graph.Lattice(dim=[50,50],nei=1,directed=False,mutual=False,circular=False)
height = 50
width = 50
border_x = range(int(width/5),width-int(width/5))
print("border x: ", border_x)
border_y = range(int(height/5),height-int(height/5))
print("border y: ", border_y)
g = dworp.Grid(height, width)
disease_agent_list = []
for i in range(height):
    for j in range(width):
        new_agent = DiseaseAgent(width, i, j)
        g.add(new_agent, i, j)
        disease_agent_list.append(new_agent)
        
for da in disease_agent_list:
    da.add_grid(g)
    
env = WeatherEnvironment(g)

border_agents = [a for a in disease_agent_list if (a.x not in border_x) and (a.y not in border_y)]
print("num border agents: ", len(border_agents))
infected_border_agents = random.sample(border_agents, int(len(border_agents)*1.0))
for i_a in infected_border_agents:
    i_a.infect()
time = dworp.BasicTime(50)
scheduler = dworp.BasicScheduler()
observer = DiseaseObserver()
sim = dworp.TwoStageSimulation(disease_agent_list, env, time, scheduler, observer)

sim.run()
