import logging
import random
from globalValues import * 

class Person():
    def __init__(self):
        """Initializes an adult person by:
        - age 
        - gender
        - kcal = kcal required per day
        - susceptibility = susceptibility to other opinions about economical, environmental and health concern
        within the household
        - concern = list of concern [env,eco,health], value between 0-1, 1 indicating a high concern

        """        
        self.age = random.randint(18, 65)
        self.gender = random.randint(0, 1) #1 is female
        self.is_adult = True
        
        self.kcal = random.gauss(2000, 500) - 500*self.gender
        self.req_servings = dict() #TODO adapt number of servings accordingly
        self.req_servings.update({FTMEAT:3})
        self.req_servings.update({FTDAIRY:3})
        self.req_servings.update({FTVEGETABLE:3})
        self.req_servings.update({FTDRYFOOD:3})
        self.req_servings.update({FTSNACKS:3})
        self.req_servings.update({FTSTOREPREPARED:3})
          
        logging.debug("Person needs %i per day", self.kcal)
        
        self.susceptibility = 0
        self.concern = [random.uniform(0.3,0.7),random.uniform(0.3,0.7),random.uniform(0.3,0.7)]
    
    
    
    
    #def old(self):
    #    self.age += 1
    #    if self.age <= 18:
    #        self.kcal += 50 + 10*self.gender
    #    elif self.age > 30 and self.age <= 40:
    #        self.kcal -= 50 + 10*self.gender
