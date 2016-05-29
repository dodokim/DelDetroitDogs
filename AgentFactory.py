"""
author = Yash Patel and DoWon Kim
name = AgentFactory.py
description = Object file for agent factory: used to produce the  
agents present in the simulation (both minority and non)
"""

import sys
import os
import math
import random
import numpy as np

import matplotlib.pyplot as plt
from operator import itemgetter
from Agent import Agent 

try:
    import networkx as nx
except ImportError: 
    raise ImportError("You must install NetworkX:\
    (http://networkx.lanl.gov/) for SE simulation")

#####################################################################
# Used to create several agents to produce the agents en masse for  #
# the setup of the simulation                                       #
#####################################################################
def AgentFactory_normint(mean, var):
    val = int(np.round(np.random.normal(mean, var)))
    if val < 0:
        return 0
    return val

def AgentFactory_invnormalize(val):
    return (5 - math.log((1/val) - 1))

class AgentFactory(object):
    def AgentFactory_createAgent(network, agentID):
        MEAN_INCOME = 50500
        VAR_INCOME = 10000

        MEAN_RES = 4
        VAR_RES = 1

        MEAN_DOG = 1
        VAR_DOG = 1

        income = AgentFactory_normint(MEAN_INCOME, VAR_INCOME)

        num_residents = AgentFactory_normint(MEAN_RES, VAR_RES)
        num_dogs = AgentFactory_normint(MEAN_DOG, VAR_DOG)

        norm_attitude = random.random()
        attitude = AgentFactory_invnormalize(norm_attitude)

        norm_education_level = random.random()
        education_level = AgentFactory_invnormalize(norm_education_level)

        p_acquire = norm_attitude/(1 + num_dogs)
        p_release = np.exp(-norm_attitude)
        p_sterilization = norm_education_level ** 2

        return Agent(agentID, income, num_residents, num_dogs, 
            attitude, p_acquire, p_release, p_sterilization, 
            education_level, network)