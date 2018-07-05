"""
Aurora's version of the environmentalism example

July 3, 2018
"""
import dworp
import igraph
import logging
import numpy as np
import sys
import os
import subprocess
# try:
#     import pygame
# except ImportError:
#     # vis will be turned off
#     print("error importing pygame: vis will be turned off")
#     pass
import pygame


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

        #lat = offsets_lon + 37.4316 # deg north
        #lon = offsets_lat + 78.6569 # deg west
        # convenience constants
        self.x = self.state[self.lon_i] - 78.6569
        self.y = self.state[self.lat_i] - 37.4316

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
        sum_for_RS = 0.0
        for i in range(0,len(neighbors)):
            nvert = neighbors[i]
            sa_array[i] = nvert["agent"].sa
            eo_array[i] = nvert["agent"].state[self.eo_i]
            ea_array[i] = nvert["agent"].state[self.ea_i]
            sum_for_EO = sum_for_EO + (sa_array[i] * eo_array[i])
            sum_for_EA = sum_for_EA + (sa_array[i] * ea_array[i])
            sum_for_denom = sum_for_denom + (sa_array[i])
            if nvert["agent"].state[self.rs_i] > 0:
                sum_for_RS = sum_for_RS + sa_array[i]
        frac_for_RS = sum_for_RS/sum_for_denom

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
                    threshval = (0.65 * (1-self.state[self.o_i]))/2
                    curval = self.state[self.cd_i] * self.state[self.eo_i] * (self.rf + self.sa + self.state[self.ea_i]) / 3.0 + 0.25*frac_for_RS
                    if curval >= threshval:
                        curprob = self.state[self.cd_i] * self.state[self.eo_i] * (self.rf + self.sa + self.state[self.ea_i]) / 3.0 + 0.25*frac_for_RS
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
    def __init__(self, fhandle):
        self.fhandle = fhandle

    def step(self, now, agents, env):
        curnum = self.computenumreusablestrawusers(now, agents, env)
        discnum =self.discontinuedreusableusers(now,agents,env)
        print("%d: current number of straw users is %d, number of adopters that no longer use is %d" %
              (now, curnum, discnum))
        self.fhandle.write("%d\t%d\t%d\n" % (now, curnum, discnum))
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
    def __init__(self,maxwithoutchange):
        self.numstepswithoutchange = 0
        self.maxstepswithoutchange = maxwithoutchange
        self.lastnumRS = 0
        self.lastdiscontinuedRS = 0

    def test(self, now, agents, env):
        curnumRS = self.computenumreusablestrawusers(agents)
        curnumdiscontinued = self.discontinuedreusableusers(agents)
        if self.lastnumRS == curnumRS:
            if self.lastdiscontinuedRS == curnumdiscontinued:
                self.numstepswithoutchange = self.numstepswithoutchange + 1
            else:
                self.numstepswithoutchange = 0
        else:
            self.numstepswithoutchange = 0
        self.lastnumRS = curnumRS
        self.lastdiscontinuedRS = curnumdiscontinued
        # check if we havent changed for too many steps
        if self.numstepswithoutchange > self.maxstepswithoutchange:
            terminate = True
        else:
            terminate = False
        if terminate:
            print("Terminating simulation early at time = {} because of persistent lack of change".format(now))
        return terminate

    def computenumreusablestrawusers(self, agents):
        count = 0
        for agent in agents:
            if agent.state[0] > 0:
                count = count + 1
        return count

    def discontinuedreusableusers(self, agents):
        count = 0
        for agent in agents:
            if agent.state[0] == 0:
                if agent.state[agent.past_i] == 1:
                    count = count + 1
        return count


class PyGameRenderer(dworp.Observer):
    def __init__(self, zoom, fps, frames_in_anim):
        self.zoom = zoom
        self.fps = fps
        self.width = 500
        self.height = 500

        pygame.init()
        pygame.display.set_caption("Reusable Straw Simulation")
        self.screen = pygame.display.set_mode((self.zoom * self.width, self.zoom * self.height))
        self.background = pygame.Surface((self.screen.get_size()))
        self.background = self.background.convert()
        self.clock = pygame.time.Clock()
        self.filename_list = [os.path.join('temp' + str(n) + '.png')
                         for n in range(frames_in_anim)]
        self.frame = 0

    def start(self, start_time, agents, env):
        self.draw(agents)

    def step(self, now, agents, env):
        self.draw(agents)

    def stop(self, now, agents, env):
        pygame.quit()

    def draw(self, agents):
        #side = self.zoom - 1
        side = 5
        self.background.fill((255, 255, 255))
        for agent in agents:
            x = self.zoom * agent.x * (0.95*self.width)
            y = self.zoom * agent.y * (0.95*self.height)
            if agent.state[agent.rs_i] == 1:
                color = (0, 191, 255)
            else:
                if agent.state[agent.past_i] == 1:
                    color = (255, 128, 0)
                else:
                    color = (139, 0, 0)
            pygame.draw.rect(self.background, color, (x, y, side, side), 0)
        self.screen.blit(self.background, (0, 0))
        pygame.font.init()  # you have to call this at the start,
        # if you want to use this module.
        myfont = pygame.font.SysFont('Arial', 24)
        textsurface = myfont.render("Simulation at %d" % (self.frame), False, (0, 0, 0))
        self.screen.blit(textsurface, (5, int(0.95*self.width)))
        pygame.display.flip()
        self.clock.tick(self.fps)
        pygame.image.save(self.screen, self.filename_list[self.frame])
        self.frame = self.frame + 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()


class RegressionTest:
    def test(self):
        lastcountshouldbe = 4

        logging.basicConfig(level=logging.WARN)
        n_tsteps = 1000
        n_tsteps = 100
        n_agents = 1000
        n_fps = 4

        mu = np.array([0.544, 0.504, 0.466, 0.482, 0.304])
        cov = np.zeros((5,5))
        cov[0,:] = [0.360000 ,0.066120,0.059520,0.093000,0.092040]
        cov[1,:] = [0.066120 ,0.336400,0.061132,0.061132,0.000000]
        cov[2,:] = [0.059520 ,0.061132,0.384400,0.042284,-0.021948]
        cov[3,:] = [0.093000 ,0.061132,0.042284,0.384400,0.098766]
        cov[4,:] = [0.092040 ,0.000000,-0.021948,0.098766,0.348100]

        scenariostr = "C"

        # n_frields: each agent has this many friends (based on the n_friends people who are geographically closest)
        if scenariostr == "A":
            n_friends = 2  # Scenario A
            outstring = "_A"
            # ensuring reproducibility by setting the seed
            np.random.seed(45)
            mu[0] = 0.25
        elif scenariostr == "B":
            n_friends = 5  # Scenario B
            # ensuring reproducibility by setting the seed
            np.random.seed(347)
            outstring = "_B"
            mu[0] = 0.50
        else:
            n_friends = 20  # Scenario C
            outstring = "_C"
            # ensuring reproducibility by setting the seed
            np.random.seed(5769)
            mu[0] = 0.75

        n_friends = 5  # constant

        personalities = np.random.multivariate_normal(mu,cov,n_agents)
        personalities[personalities > 1] = 1.0
        personalities[personalities < 0] = 0.0
        wealth = np.random.normal(300000,100000,n_agents)
        wealth[wealth > 600000] = 600000
        wealth[wealth < 10000]  = 10000
        offsets_lat = np.random.random((n_agents,1))
        offsets_lon = np.random.random((n_agents,1))
        lat = offsets_lon + 37.4316 # deg north
        lon = offsets_lat + 78.6569 # deg west
        gender = np.random.randint(0,1,(n_agents,1))
        education = np.random.randint(0,4,(n_agents,1))
        #colddrinks = np.random.normal(0.80,0.15,n_agents)
        colddrinks = np.random.normal(0.90, 0.1, n_agents)
        colddrinks[colddrinks > 1] = 1
        colddrinks[colddrinks < 0] = 0

        #eatingout = np.random.normal(0.70,0.10,n_agents)
        eatingout = np.random.normal(0.90,0.10,n_agents)
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
        outname = "outputs%s.tsv" % (outstring)
        fhandle = open(outname,'w')
        myobserver = EEObserver(fhandle)

        #vis_flag = args.vis and 'pygame' in sys.modules
        vis_flag = False and 'pygame' in sys.modules
        if vis_flag:
            print("vis_flag is True")
        else:
            print("vis_flag is False")
        # vis does not support different colors
        #colors = ["blue", "orange"]
        #params = SegregationParams(density, similarity, grid_size, seed, colors)

        # create and run one realization of the simulation
        observer = dworp.ChainedObserver(
            myobserver,
        )
        if vis_flag:
            observer.append(dworp.PauseAtEndObserver(3))
            pgr = PyGameRenderer(1, n_fps, n_tsteps+1)
            observer.append(pgr)

        term = EETerminator(100)
        sim = dworp.BasicSimulation(agents, env, time, scheduler, observer,terminator=term)
        sim.run()
        fhandle.close()

        if vis_flag:
            filename_list = pgr.filename_list
            seconds_per_frame = 1.0/n_fps
            frame_delay = str(int(seconds_per_frame * 100))
            #command_list = ['convert', '-delay', frame_delay, '-loop', '0'] + filename_list + ['anim.gif']
            command_list = ['convert', '-delay', frame_delay, '-loop', '0'] + filename_list + ['anim%s.gif' % (outstring)]
            try:
                # Use the "convert" command (part of ImageMagick) to build the animation
                subprocess.call(command_list)
            except:
                print("couldnt create the animation")
                pass
            # Earlier, we saved an image file for each frame of the animation. Now
            # that the animation is assembled, we can (optionally) delete those files
            if True:
                for filename in filename_list:
                    os.remove(filename)
            return

        lastcount = myobserver.computenumreusablestrawusers(0,agents,env)
        print("Last Count = %d" % (lastcount))
        if lastcount == lastcountshouldbe:
            print("Regression test passed!")
            return True
        else:
            print("Regression test failed! last count should be %d" % (lastcountshouldbe))
            return False


thistest = RegressionTest()
thistest.test()