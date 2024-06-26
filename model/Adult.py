import json
import logging
import random
import globals
from FoodGroups import FoodGroups
from Person import Person
class Adult(Person):
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
        super().__init__()  
        self.age = random.randint(globals.ADULT_AGE_MIN,globals.ADULT_AGE_MAX)
        self.is_adult = True
        self.kcal = random.gauss(2000, 500) - 500*self.gender
        
        #logging.debug("Person needs %i per day", self.kcal)
        
        if self.gender == globals.MALE: 
            veg_servings = random.uniform(globals.ADULT_MALE_VEG_SERVINGS_MIN, globals.ADULT_FEMALE_VEG_SERVINGS_MAX)
            dry_food_servings = random.uniform(globals.ADULT_MALE_DRY_FOOD_SERVINGS_MIN, globals.ADULT_FEMALE_DRY_FOOD_SERVINGS_MAX)
            dairy_servings = random.uniform(globals.ADULT_MALE_DAIRY_SERVINGS_MIN, globals.ADULT_FEMALE_DAIRY_SERVINGS_MAX)
            meat_servings = random.uniform(globals.ADULT_MALE_MEAT_SERVINGS_MIN, globals.ADULT_FEMALE_MEAT_SERVINGS_MAX)
            snacks_servings = random.uniform(globals.ADULT_MALE_SNACKS_SERVINGS_MIN, globals.ADULT_FEMALE_SNACKS_SERVINGS_MAX)
            store_prepared_servings = random.uniform(globals.ADULT_MALE_STORE_PREPARED_SERVINGS_MIN, globals.ADULT_FEMALE_STORE_PREPARED_SERVINGS_MAX)
        else: #FEMALE
            veg_servings = random.uniform(globals.ADULT_MALE_VEG_SERVINGS_MIN, globals.ADULT_FEMALE_VEG_SERVINGS_MAX)
            dry_food_servings = random.uniform(globals.ADULT_MALE_DRY_FOOD_SERVINGS_MIN, globals.ADULT_FEMALE_DRY_FOOD_SERVINGS_MAX)
            dairy_servings = random.uniform(globals.ADULT_MALE_DAIRY_SERVINGS_MIN, globals.ADULT_FEMALE_DAIRY_SERVINGS_MAX)
            meat_servings = random.uniform(globals.ADULT_MALE_MEAT_SERVINGS_MIN, globals.ADULT_FEMALE_MEAT_SERVINGS_MAX)
            snacks_servings = random.uniform(globals.ADULT_MALE_SNACKS_SERVINGS_MIN, globals.ADULT_FEMALE_SNACKS_SERVINGS_MAX)
            store_prepared_servings = random.uniform(globals.ADULT_MALE_STORE_PREPARED_SERVINGS_MIN, globals.ADULT_FEMALE_STORE_PREPARED_SERVINGS_MAX)
            
        food_groups = FoodGroups.get_instance()
        self.req_servings = veg_servings + dry_food_servings + dairy_servings + meat_servings + snacks_servings + store_prepared_servings
        sum_pref = sum(self.fg_preference.values())
        self.req_servings_per_fg = dict()
        for item in food_groups.get_all_food_groups(): 
            self.req_servings_per_fg.update({item:(self.req_servings/sum_pref)*self.fg_preference[item]})
        
        self.susceptibility = 0
        self.concern = [random.uniform(globals.ADULT_CONCERN_MIN,globals.ADULT_CONCERN_MAX),random.uniform(globals.ADULT_CONCERN_MIN,globals.ADULT_CONCERN_MAX),1- random.uniform(globals.ADULT_CONCERN_MIN,globals.ADULT_CONCERN_MAX)]
        self.plate_waste_ratio = random.uniform(globals.ADULT_PLATE_WASTE_MIN, globals.ADULT_PLATE_WASTE_MAX)
        