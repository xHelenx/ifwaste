import logging
import random
import globals

class Person():
    def __init__(self):
        """Initializes an adult person by:
        - age 
        - gender
        - kcal = kcal required per day
        - susceptibility = susceptibility to other opinions about economical, environmental and health concern
        within the household
        - concern = list of concern [env,eco,health], value between 0-1, 1 indicating a high concern
        - req_serving = requried servings per food type 
        - plate waste ratio 
        """        
        self.age = random.randint(globals.ADULT_AGE_MIN,globals.ADULT_AGE_MAX)
        self.gender = random.randint(globals.MALE, globals.FEMALE) #1 is female
        self.is_adult = True
        
        self.kcal = random.gauss(2000, 500) - 500*self.gender
        self.req_servings = dict() 
        if self.gender == globals.MALE: 
            veg_servings = random.uniform(2.6,2.9)
            dry_food_servings = random.uniform(7.3,8)
            dairy_servings = random.uniform(1.9,2)
            meat_servings = 8
            snacks_servings = 0
            store_prepared_servings = 0
        else: #FEMALE
            veg_servings = random.uniform(2.5,2.8)
            dry_food_servings = random.uniform(5.3,6)
            dairy_servings = 1.3
            meat_servings = random.uniform(5.2,5.5)
            snacks_servings = 0
            store_prepared_servings = 0
        
        
        self.req_servings.update({globals.FTVEGETABLE:veg_servings})
        self.req_servings.update({globals.FTDRYFOOD:dry_food_servings})
        self.req_servings.update({globals.FTDAIRY:dairy_servings})
        self.req_servings.update({globals.FTMEAT:meat_servings})
        self.req_servings.update({globals.FTSNACKS:snacks_servings})
        self.req_servings.update({globals.FTSTOREPREPARED:store_prepared_servings})
          
        logging.debug("Person needs %i per day", self.kcal)
        
        self.susceptibility = 0
        self.concern = [random.uniform(globals.ADULT_CONCERN_MIN,globals.ADULT_CONCERN_MAX),random.uniform(globals.ADULT_CONCERN_MIN,globals.ADULT_CONCERN_MAX),random.uniform(globals.ADULT_CONCERN_MIN,globals.ADULT_CONCERN_MAX)]
        self.plate_waste_ratio = random.uniform(globals.ADULT_PLATE_WASTE_MIN,globals.ADULT_PLATE_WASTE_MAX)
    
    #def old(self):
    #    self.age += 1
    #    if self.age <= 18:
    #        self.kcal += 50 + 10*self.gender
    #    elif self.age > 30 and self.age <= 40:
    #        self.kcal -= 50 + 10*self.gender
