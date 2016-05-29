"""
author = Yash Patel and DoWon Kim
name = DogControlSimulation.py
description: Contains all the methods pertinent to producing the
simulation for modelling the relation between sexual minorities
and depression (SMD simulation)
"""

import sys
import os
import csv
import random,itertools
import numpy as np

from NetworkBase import NetworkBase
from ERNetwork import ERNetwork
from ASFNetwork import ASFNetwork
from SWNetwork import SWNetwork

import matplotlib.pyplot as plt
from operator import itemgetter 

try:
    import networkx as nx
except ImportError:
    raise ImportError("You must install NetworkX:\
    (http://networkx.lanl.gov/) for SE simulation")

class DogSimulationModel:
    #################################################################
    # Given the type of network, the simulation time span, and count#
    # of agents in the network, a simulation is created and run for #
    # testing depression as a function of minority prevalence. Also #
    # have control on the impact ratings of each of the parameters: #
    # defaults have been provided                                   #
    #################################################################
    def __init__(self, networkType='ER', timeSpan=10, numAgents=10):
        self.networkType = networkType
        self.timeSpan = timeSpan
        self.numAgents = numAgents

        self.DogModel_setNetwork()
        
    #################################################################
    # Based on the specified value of the network type, generates   #
    # and sets the network accordingly. Sets the initial value of   #
    # simulation to those specified in the parameters (attitude_0   #
    # corresponds to initial value of attitude, etc...)             #
    #################################################################
    def DogModel_setNetwork(self):
        if self.networkType == 'ER':
            self.network = ERNetwork(self.numAgents, self.timeSpan)
        elif self.networkType == 'SW':
            self.network = SWNetwork(self.numAgents, self.timeSpan)
        else:
            self.network = ASFNetwork(self.numAgents, self.timeSpan)

    #################################################################
    # Writes the header of the CSV file to be given as output in the#
    # specified file                                                #
    #################################################################
    def DogModel_writeSimulationHeader(self, resultsFile):
        if resultsFile is not None:
            columns = ['time', 'agentID', 'stray_dogs', 
            'attitude', 'prob_acquire', 'prob_release', 
            'norm_education_level']
            with open(resultsFile, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(columns)

    #################################################################
    # Writes the current data/parameters corresponding to each agent#
    # in the network at the current time step, given the current    #
    # time in the simulation and the file to be written to          #
    #################################################################
    def DogModel_writeSimulationData(self, time, resultsFile):
        if resultsFile is not None:
            with open(resultsFile, 'a') as f:
                writer = csv.writer(f)
                Agents = self.network.networkBase.Agents
                for agent in Agents:
                    curAgent = Agents[agent]
                    row = [time, curAgent.agentID, curAgent.num_stray_dogs, 
                        curAgent.normal_attitude, curAgent.p_acquire, 
                        curAgent.p_release, curAgent.norm_education_level]

                    writer.writerow(row)

    #################################################################
    # Runs simulation over the desired timespan and produces/outputs#
    # results in CSV file specified along with displaying graphics  #
    #################################################################
    def DogModel_runSimulation(self, resultsFile):
        self.DogModel_writeSimulationHeader(resultsFile)

        # Converts from years to "ticks" (represent 2 week span)
        numTicks = self.timeSpan * 26
        pos = nx.random_layout(self.network.G)
        for i in range(0, self.timeSpan):
            if i % 10 == 0:
                self.DogModel_writeSimulationData(i, resultsFile)   

                print("Plotting time step {}".format(i))
                self.network.networkBase.\
                    NetworkBase_visualizeNetwork(False, i, pos)
            self.network.networkBase.NetworkBase_timeStep(i)

#####################################################################
# Given the paramters of the simulation (upon being prompted on)    #
# command line, runs simulation, outputting a CSV with each time    #
# step and a graphical display corresponding to the final iteration #   
#####################################################################
def main():
    # ER, SW, or ASF
    networkType = "ER"
    timeSpan = 50
    numAgents = 15

    resultsFile = "Results\\TimeResults\\results.csv"
    simulationModel = DogSimulationModel(networkType, timeSpan, numAgents)
    simulationModel.DogModel_runSimulation(resultsFile)

    print("Terminating simulation...")

if __name__ == "__main__":
    main()