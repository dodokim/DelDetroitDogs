"""
author = Yash Patel and DoWon Kim
name = SWNetwork.py
description: Contains all the methods pertinent to modelling SW
network (small world)
"""

import sys
import os
import random,itertools
from numpy import array, zeros, std, mean, sqrt

from NetworkBase import NetworkBase
from AgentFactory import AgentFactory
from Agent import Agent

import matplotlib.pyplot as plt
from operator import itemgetter 

try:
    import networkx as nx
except ImportError:
    raise ImportError("You must install NetworkX:\
    (http://networkx.lanl.gov/) for SE simulation")

class SWNetwork:
    #################################################################
    # Given a nodeCount for the number of agents to be simulated,   #
    # number of coaches maximally present in the simulation, the    #
    # probability of adding a new edge for each edge present to     #
    # other nodes (defaulted to .0), and the number of neighbors to #
    # which each node is to be connected (k) initializes SW Network #
    #################################################################
    def __init__(self, nodeCount, timeSpan, k=4, p = 0.0):
        self.nodeCount = nodeCount

        self.k = k
        self.p = p
        self.agentFactory = AgentFactory
        
        self.Agents = {}
        self.networkBase = NetworkBase("SWNetwork", timeSpan)

        self.SWNetwork_createAgents()

        # Sets the network base to have the agents just created and
        # the graph just generated and then choosing discriminating
        # portion of the population
        self.networkBase.NetworkBase_setGraph(self.G)
        self.networkBase.NetworkBase_setAgents(self.Agents)
        self.networkBase.NetworkBase_setupLookup()

    #################################################################
    # Creates the agents present in the simulation (SW graph)       #
    #################################################################
    def SWNetwork_createAgents(self):
        self.G = nx.generators.random_graphs.watts_strogatz_graph(
                    n = self.nodeCount,
                    k = self.k,
                    p = self.p,
                    seed = None)
        self.G.name = "small_world_graph(%s,%s,%s)"%(self.nodeCount, \
            self.k, self.p)

        for i in range(0, self.nodeCount):    
            curAgent = self.agentFactory.AgentFactory_createAgent(self, i)
            self.Agents[curAgent.agentID] = curAgent