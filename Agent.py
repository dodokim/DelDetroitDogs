"""
author = Yash Patel and DoWon Kim
name = BaseAgent.py
description: Object file containing all the methods modelling a
generic agent in the simulation. Agents comprise the households 
in the simulation, with Dogs as a relevant object houses own
"""

import sys
import os
import math
import random
import numpy as np

from NetworkBase import NetworkBase
import matplotlib.pyplot as plt
from operator import itemgetter 
from collections import OrderedDict

from Dog import Dog

try:
    import networkx as nx
except ImportError:
    raise ImportError("You must install NetworkX:\
    (http://networkx.lanl.gov/) for SE simulation")

#####################################################################
# A generic base model for agents of the simulation: used to model  #
# the constituent people in a population                            #
#####################################################################
class Agent:
    def __init__(self, agentID, income, num_residents, num_dogs, 
        attitude, p_acquire, p_release, p_sterilization, 
        education_level, network):
        # --------------------- static variables ------------------- #
        # arbitrary value for identification
        self.agentID = agentID

        # income of household
        self.income = income

        # number of people staying in house -- maximum around 4
        self.num_residents = num_residents

        # number of dogs owned -- length of dogs array
        self.num_dogs = num_dogs
        self.dogs = []

        # number of stray dogs "at the household" (i.e. at house vertex)
        self.num_stray_dogs = 0

        # whether the household has a stray dog -- if #stray > 0
        self.has_stray_dog = False

        # network used for connections in simulation
        self.network = network
        
        # ------------------- changing variables ------------------- #
        # whether or not the household has children (i.e. 
        # > 2 people, assuming no grandparents)
        self.has_children = (self.num_residents > 2)

        # list of associated friends in the network
        self.friends = []

        # un-normalized attitude value of household towards dogs
        self.attitude = attitude
    
        # normalized attitude on [0, 1] scale (logistic)
        self.normal_attitude = self.Agent_normalize(self.attitude)

        # probability of getting another dog (NOT by reproduction)
        self.p_acquire = p_acquire

        # probabilty of letting go of a currently owned dog
        self.p_release = p_release

        # probability of steralizing dogs
        self.p_sterilization = p_sterilization
        
        # un-normalized level of education
        self.education_level = education_level

        # normalized education level on [0, 1] scale (logistic)
        self.norm_education_level = \
            self.Agent_normalize(self.education_level)

        # list of dogs that are owned by household
        for i in range(0, num_dogs):
            self.Agent_new_dog()
            
    #################################################################
    # Provides an output string for printing out agents             #
    #################################################################
    def __str__(self):
        return ("Attitude: {}\n, Probability of Acquiring: {}\n,"  
            "Probability of Release: {}\n, Probability of "
            "Steralizing: {}\n, Education: {}\n".format(normal_attitude, 
            p_acquire, p_release, p_sterilization, norm_education_level))

    def Agent_normalize(self, val):
        return 1/(1 + np.exp(-(val - 5)))

    #################################################################
    # Used for initialization of ASF network: determines to which   #
    # nodes a given agent will attach (based on connection density).#
    # Please note: the following function was taken from Steve      #
    # Mooney's Obesagent ASFNetwork.py program                      #
    #################################################################
    def Agent_preferentiallyAttach(self, network, nConnections):
        candidate_nodes = network.G.nodes()
        
        # Reorder candidates to ensure randomness
        random.shuffle(candidate_nodes)
        target_nodes = []

        # Double edge count to get per-node edge count.
        edge_count = len(network.G.edges(candidate_nodes)) * 2

        # Pick a random number
        rand = random.random()
        p_sum = 0.0
        
        # To add edges per the B-A algorithm, we compute probabilities
        # for each node multiplying by nConnections, then partition the
        # probability space per the probabilities.  Every time we find a
        # match, we add one to the random number.  So, for example, 
        # suppose we have four nodes with p1=0.5, p2=0.75, p3=0.5 and 
        # p4=0.25.  If our random number is 0.38, we'll first pick node 1, 
        # since 0 < .38 < .5, then skip node 2, since 1.38 > 1.25 
        # (=0.5+0.75), then pick node 3, since 1.25 < 1.38 < 1.75, then 
        # skip node 4, since 2.38 > 2.0

        # Note that because we randomized candidates above, the selection is
        # truly random.

        for i in range(len(candidate_nodes)):
            candidate_node = candidate_nodes[i]
            candidate_edges = network.G.edges(candidate_node)
            p_edge = nConnections * 1.0 * len(candidate_edges)/edge_count
            low = p_sum
            high = p_sum + p_edge
            test = rand + len(target_nodes)
            if (test > low and test <= high):
                target_nodes.append(candidate_node)
            p_sum += p_edge

        node_list = [self.agentID] * len(target_nodes)
        edges_to_add = zip(node_list, target_nodes)
        network.networkBase.NetworkBase_addEdges(edges_to_add)

    def Agent_updateAgent(self):
        self.Agent_update_attitude()
        self.Agent_update_probacquire()
        self.Agent_update_probrelease()
        self.Agent_update_education()
        self.Agent_update_steralize()

        self.Agent_acquire_dog()
        for dog in self.dogs:
            self.Agent_steralize_dog(dog)
            self.Agent_release_dog(dog)
        self.Agent_update_stray()

    def Agent_new_dog(self):
        dog = Dog(self, self.agentID)
        self.dogs.append(dog)
        self.num_dogs += 1

        self.network.networkBase.dogs.append(dog)
        self.network.networkBase.num_dogs += 1

    def Agent_acquire_dog(self):
        if random.random() < self.p_acquire:
            self.Agent_new_dog()

    def Agent_release_dog(self, dog):
        if random.random() < self.p_release:
            self.dogs.remove(dog)
            self.num_dogs -= 1
            dog.owner = None

            self.network.networkBase.NetworkBase_addStray(
                self.agentID, dog)

    def Agent_steralize_dog(self, dog):
        if random.random() < self.p_sterilization:
            dog.is_steralized = True
        
    def Agent_update_attitude(self):
        delta_attitude = self.norm_education_level/(1 + 
            self.num_stray_dogs)
        delta_attitude *= self.network.networkBase.\
            NetworkBase_mean_attitude(self)

        self.attitude += delta_attitude
        self.normal_attitude = self.Agent_normalize(self.attitude)

    def Agent_update_probacquire(self):
        self.p_acquire = self.normal_attitude/(1 + self.num_dogs)

    def Agent_update_probrelease(self):
        self.p_release = np.exp(-self.normal_attitude)

    def Agent_update_education(self):
        delta_education = self.network.networkBase.\
            NetworkBase_mean_education(self)
        delta_education += self.network.networkBase.\
            dog_education * (1 - (self.norm_education_level - .5) ** 2)

        self.education_level += delta_education
        self.norm_education_level = self.Agent_normalize(self.education_level)

    def Agent_update_steralize(self):
        self.p_sterilization = self.norm_education_level ** 2

    def Agent_update_stray(self):
        strays = self.network.networkBase.NetworkBase_getStray(self.agentID)
        self.num_stray_dogs = len(strays)
        self.has_stray_dog = (self.num_stray_dogs > 0)