import random
from Person import Person
from globalValues import * 


class Child(Person):
    def __init__(self):
        """Initializes a child by:
        - age 
        - gender
        - kcal = kcal required per day
        - susceptibility = susceptibility to other opinions about economical, environmental and health concern
        within the household
        - concern = list of concern [env,eco,health], value between 0-1, 1 indicating a high concern

        """ 
        super().__init__()
        self.age = random.randint(1, 18)
        self.is_adult = False 
        
        self.kcal = random.gauss(1200, 200) + self.age*50
        self.req_servings = dict() #TODO adapt number of servings accordingly
        self.req_servings.update({FTMEAT:5})
        self.req_servings.update({FTDAIRY:5})
        self.req_servings.update({FTVEGETABLE:5})
        self.req_servings.update({FTDRYFOOD:5})
        self.req_servings.update({FTSNACKS:5})
        self.req_servings.update({FTSTOREPREPARED:5})
          
        
        self.susceptibility = 0
        self.concern = [random.uniform(0,0.3),random.uniform(0,0.3),random.uniform(0,0.3)]