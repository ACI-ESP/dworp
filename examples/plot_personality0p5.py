"""
JHU/APL's red blue challenge, environmentalism product adoption example

Major Dependencies: Dworp, (pip install dworp, source code available at https://github.com/ACI-ESP/dworp)
                  *  pygame (for plotting)
                  *  ImageMagick, to run commandline convert to create an animated gif from output png images
    (note that pygame and ImageMagick are optional, the script will still run, but plotting would be limited)

Usage:
  (debugging mode, default) > python -m pdb environmentalismexample.py vsn=A vis=0
  (nondebugging mode) > python environmentalismexample.py vsn=B vis=1 dbg=0

  The input argument vsn = A, B, or C determines which scenario is run. The default is B.
  The input argument vis = 0 or 1 determines whether to try to plot (0 = no, 1 = yes, default is 1)

Scenario: A group of social science researchers (you) would like to study how the movement to get people to use
  reusable straws is spreading.

Questions Posed:
  What factors into a person’s decision to change their behavior and use reusable straws?
  What could be done to increase the usage of reusable straws?

Aurora.Schmidt@jhuapl.edu
240-228-1635
Christian.Sun@jhuapl.edu
Aspire Intern
July 3, 2018
"""
import numpy as np
import sys
import os
import pdb
import matplotlib
import matplotlib.pyplot as plt

pathtofolder = '/Users/schmiac1/Desktop/StrawWorld'

files = os.listdir(pathtofolder)

iternums = []
toplotfiles = []
RS_matrix = np.zeros((10,25))
nolongerRS_matrix = np.zeros((10,25))
for i in range(0,len(files)):
    if len(files[i])>7:
        if files[i][0:7]=="outputs":
            parts = files[i].split('B')
            numparts = parts[1].split('.')
            iternum = int(numparts[0])
            iternums.append(iternum)
            toplotfiles.append(files[i])
            with open(pathtofolder+"/"+files[i],'r') as f:
                for k in range(0,10000):
                    curline = f.readline()
                    if curline == "":
                        break
                    if curline == -1:
                        break
                    parts = curline.split()
                    RS_matrix[iternum,k] = int(parts[1])
                    nolongerRS_matrix[iternum,k] = int(parts[2])
                f.close()
RS_mean = []
for i in range(0,25):
    RS_mean.append( np.mean(RS_matrix[:,i]))


pathtofolder = '/Users/schmiac1/Desktop/StrawWorld/Personality0p5'
files2 = os.listdir(pathtofolder)

iternums2 = []
toplotfiles2 = []
RS_matrix2 = np.zeros((10,25))
nolongerRS_matrix2 = np.zeros((10,25))
for i in range(0,len(files2)):
    if len(files2[i])>7:
        if files2[i][0:7]=="outputs":
            parts = files2[i].split('B')
            numparts = parts[1].split('.')
            iternum = int(numparts[0])
            iternums2.append(iternum)
            toplotfiles.append(files2[i])
            with open(pathtofolder+"/"+files2[i],'r') as f:
                for k in range(0,10000):
                    curline = f.readline()
                    if curline == "":
                        break
                    if curline == -1:
                        break
                    parts = curline.split()
                    RS_matrix2[iternum,k] = int(parts[1])
                    nolongerRS_matrix2[iternum,k] = int(parts[2])
                f.close()
RS_mean2 = []
for i in range(0,25):
    RS_mean2.append( np.mean(RS_matrix2[:,i]))


# Data for plotting
t = range(1,26)

# Note that using plt.subplots below is equivalent to using
# fig = plt.figure() and then ax = fig.add_subplot(111)
fig, ax = plt.subplots()
for i in range(0,len(iternums)):
    ax.plot(t, RS_matrix[i,:],'b--',linewidth=0.5)
ax.plot(t,RS_mean2,'k')
ax.plot(t,RS_mean,'b.-',linewidth=0.5, label='Original Reputation Parameters')
for i in range(0,len(iternums2)):
    ax.plot(t, RS_matrix2[i,:],'r--',linewidth=0.5)
ax.plot(t,RS_mean2,'k')
ax.plot(t,RS_mean2,'r.-',linewidth=0.5, label='Reputation Focus = 0')

ax.set(xlabel='Time-step', ylabel='Number of Users',
       title='Number of Users of Reusable Straws vs Time-step')
#ax.grid()
ax.legend()
fig.savefig("comparison_Personality0p5.png")
plt.show()

pdb.set_trace()