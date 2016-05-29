"""
author = Yash Patel and DoWon Kim
name = NetworkBase.py
description: Contains all the methods pertinent to the network
base model, used to produce the other graphs desired to simulate
"""

import sys
import os
import random
import numpy as np

import matplotlib.pyplot as plt
from operator import itemgetter 

try:
    import networkx as nx
except ImportError:
    raise ImportError("You must install NetworkX:\
    (http://networkx.lanl.gov/) for SE simulation")

class NetworkBase:
    #################################################################
    # Initializes the base of the network with the type it is to be #
    # i.e. SW, ER, etc... and number of coaches                     #
    #################################################################
    def __init__(self, networkType, timeSpan):
        self.networkType = networkType
        self.timeSpan = timeSpan

        self.dogs = []
        self.stray_dogs = []

        self.num_dogs = 0
        self.stray_to_loc = {}
        self.loc_to_stray = {}

        self.dog_education = 0

    def NetworkBase_timeStep(self, time): 
        for agent in self.NetworkBase_getAgents():
            agent.Agent_updateAgent()

        for dog in self.dogs:
            dog.Dog_reproduce()

        for stray in self.stray_dogs:
            self.NetworkBase_spreadStray(stray)
        self.NetworkBase_updateEducation(time)

    def NetworkBase_setupLookup(self):
        for agent in self.Agents:
            self.loc_to_stray[agent] = []

    def NetworkBase_updateEducation(self, time):
        if time < self.timeSpan/2:
            return
        self.dog_education += 2/self.timeSpan
        
    #################################################################
    # Given a graph G, assigns it to be the graph for this network  #
    #################################################################
    def NetworkBase_setGraph(self, G):
        self.G = G

    #################################################################
    # Given dictionary of agents, assigns them for this network     #
    #################################################################
    def NetworkBase_setAgents(self, agents):
        self.Agents = agents

    #################################################################
    # Given a list of nodes, adds edges between all of them         #
    #################################################################
    def NetworkBase_addEdges(self, nodeList):
        self.G.add_edges_from(nodeList)

    #################################################################
    # Given two agents in the graph, respectively with IDs agentID1 #
    # and agentID2, removes the edge between them                   #
    #################################################################
    def NetworkBase_removeEdge(self, agentID1, agentID2):
        self.G.remove_edge(agentID1, agentID2)

    #################################################################
    # Returns all the edges present in the graph associated with the#
    # network base                                                  #
    #################################################################
    def NetworkBase_getEdges(self):
        return self.G.edges()

    #################################################################
    # Returns the agent associated with the agentID specified       #
    #################################################################
    def NetworkBase_getAgent(self, agentID):
        return self.Agents[agentID]

    def NetworkBase_getAgents(self):
        return [self.Agents[agent] for agent in self.Agents]

    def NetworkBase_addStray(self, agentID, dog):
        self.stray_dogs.append(dog)

        self.stray_to_loc[dog] = agentID
        self.loc_to_stray[agentID].append(dog)

    def NetworkBase_getStray(self, agentID):
        return self.loc_to_stray[agentID]

    def NetworkBase_spreadStray(self, stray):
        agentID = self.stray_to_loc[stray]
        neighbors = self.NetworkBase_getNeighbors(
            self.NetworkBase_getAgent(agentID))
        rand = int(len(neighbors) * random.random())
        move_agent = neighbors[rand]

        self.stray_to_loc[stray] = move_agent
        stray.loc = move_agent

        self.loc_to_stray[move_agent].append(stray)
        self.loc_to_stray[agentID].remove(stray)

    #################################################################
    # Returns the total number of agents in the graph associated w/ #
    # the network base                                              #
    #################################################################
    def NetworkBase_getNumAgents(self):
        return len(self.Agents)

    #################################################################
    # Returns an array of those in the "social network" of a given  #
    # agent, defined as being those separated by, at most, two      #
    # degrees in the graph (two connections away)                   #
    #################################################################
    def NetworkBase_getNeighbors(self, agent):
        agentID = agent.agentID
        return nx.neighbors(self.G, agentID)

    def NetworkBase_mean_attitude(self, agent):
        neighbors = self.NetworkBase_getNeighbors(agent)
        attitudes = [self.NetworkBase_getAgent(neigh).attitude 
            for neigh in neighbors]
        return np.mean(attitudes)

    def NetworkBase_mean_education(self, agent):
        neighbors = self.NetworkBase_getNeighbors(agent)
        educations = [self.NetworkBase_getAgent(neigh).education_level 
            for neigh in neighbors]
        return np.mean(educations)

    #################################################################
    # Assigns to each nodes the appropriate visual attributes, with #
    # those nodes with wellness coaches given a color of red and    #
    # those without blue along with an opacity corresponding to SE  #
    #################################################################
    def NetworkBase_addVisualAttributes(self):
        MAX_STRAY = 10

        # Iterate through each of the nodes present in the graph and
        # finds respective agent
        for agentID in self.G.nodes():
            curAgent = self.Agents[agentID]

            el = self.NetworkBase_getAgent(agentID).norm_education_level
            stray = len(self.NetworkBase_getStray(agentID))/MAX_STRAY

            if int(el) == 1: el = 1
            if int(stray) == 1: stray = 1

            # Marks depressed agents as red nodes and blue otherwise
            self.G.node[agentID]['color'] = el

            # Makes concealed agents less "visible" in display 
            self.G.node[agentID]['opacity'] = stray

    #################################################################
    # Provides graphical display of the population, color coded to  #
    # illustrate who does and doesn't have the wellness coaches and #
    # sized proportional to the level of exercise. Pass in True for #
    # toShow to display directly and False to save for later view   #
    # with the fileName indicating the current timestep simulated.  #
    # pos provides the initial layout for the visual display        #
    #################################################################
    def NetworkBase_visualizeNetwork(self, toShow, time, pos):
        self.NetworkBase_addVisualAttributes()
        
        plt.figure(figsize=(12,12))
        for node in self.G.nodes():
            nx.draw_networkx_nodes(self.G,pos, nodelist=[node], 
                node_color=self.G.node[node]['color'],
                node_size=500, node_shape='o', 
                alpha=self.G.node[node]['opacity'])
        nx.draw_networkx_edges(self.G,pos,width=1.0,alpha=.5)

        plt.title("Dog Control at Time {}".format(time))
        plt.savefig("Results\\TimeResults\\timestep{}.png".format(time))
        if toShow: 
            plt.show()
        plt.close()