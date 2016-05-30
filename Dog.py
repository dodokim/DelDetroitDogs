"""
author = Yash Patel and DoWon Kim
name = Dog.py
description: 
"""

import random
import numpy as np
MIN_GESTATION = 5

class Dog:
    def __init__(self, owner, network, loc):
        self.owner = owner
        self.network = network
        self.loc = loc
        
        self.prob_rand_reproduce = random.random()
        self.prob_reproduce = self.Dog_update_reproduce()
        self.is_steralized = False

        self.last_birth = float("inf")

    def Dog_update_reproduce(self):
        self.prob_rand_reproduce = \
            random.uniform(self.prob_rand_reproduce, 1)
        el_factor = 1
        if self.owner is not None:
        	el_factor = self.owner.norm_education_level
        self.prob_reproduce = 1/(1 + 10 * el_factor *
            np.exp(-self.prob_rand_reproduce/2))

    def Dog_reproduce(self):
        if self.is_steralized:
            return

        self.last_birth += 1
        rand = random.random()

        if self.last_birth > MIN_GESTATION:
            self.Dog_update_reproduce()

        # produces new dog (i.e. has reproduced)
        if rand < self.prob_reproduce:
            if self.owner is not None:
                self.owner.Agent_new_dog()
            else:
                dog = Dog(None, self.network, self.loc)
                self.network.networkBase.dogs.append(dog) 
                self.network.networkBase.num_dogs += 1
                self.network.networkBase.NetworkBase_addStray(
                	self.loc, dog)
            
            self.prob_rand_reproduce = 0
            self.prob_reproduce = 0
            self.last_birth = 0