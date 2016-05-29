"""
author = Yash Patel and DoWon Kim
name = ASFNetwork.py
description = Contains all the methods pertinent to modelling ASF 
network (small world)
"""

import sys
import os
import random,itertools
from copy import deepcopy
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

class ASFNetwork:
    #################################################################
    # Given a nodeCount for the number of agents to be simulated,   #
    # number of coaches maximally present in the simulation, the    #
    # number of baseline nodes of the graph (m_0), and number       #
    # of edges to be added at each step of the initialization (m)   #
    # produces an ASF network                                       #
    #################################################################
    def __init__(self, nodeCount, timeSpan, m_0 = 4, m = 4):
        self.nodeCount = nodeCount

        self.m_0 = m_0
        self.m = m
        self.agentFactory = AgentFactory

        self.Agents = {}
        self.networkBase = NetworkBase("ASFNetwork", timeSpan)
        
        self.ASFNetwork_createAgents()

        # Sets the network base to have the agents just created and
        # the graph just generated and then choosing discriminating
        # portion of the population
        self.networkBase.NetworkBase_setAgents(self.Agents)
        self.networkBase.NetworkBase_setupLookup()
    
    #################################################################
    # Creates the agents present in the simulation (ASF graph)      #
    #################################################################
    def ASFNetwork_createAgents(self):
        # Creates baseline nodes (from m_0 specified)
        totalConnect = self.m_0

        self.G = nx.Graph()
        self.networkBase.NetworkBase_setGraph(self.G)
        
        self.G.name = "barabasi_albert_graph(%s,%s)"\
            %(self.m,self.nodeCount)

        for i in range(0, totalConnect):
            curAgent = self.agentFactory.AgentFactory_createAgent(self, i)
            self.Agents[i] = curAgent
            self.G.add_node(curAgent.agentID)
        
        for i in range(0, totalConnect):
            for j in range(i, totalConnect):
                self.G.add_edge(i,j)
    
        # Creates remainder of nodes (assigning them to agents)
        for i in range(totalConnect, self.nodeCount):
            curAgent = self.agentFactory.AgentFactory_createAgent(self, i)
            self.Agents[i] = curAgent
            self.G.add_node(curAgent.agentID)
            curAgent.Agent_preferentiallyAttach(self, self.m)