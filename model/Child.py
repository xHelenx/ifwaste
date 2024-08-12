import random
from Person import Person
import globals
import json

from FoodGroups import FoodGroups 

class Child(Person):
    def __init__(self) -> None:
        """Initializes a child by:
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
        self.age:int = random.randint(2, 18)
        self.is_adult:bool = False 
        self.kcal:float = random.gauss(1200, 200) + self.age*50

        if self.gender == globals.MALE: 
            veg_servings = random.uniform(globals.CHILD_MALE_VEG_SERVINGS_MIN, globals.CHILD_FEMALE_VEG_SERVINGS_MAX)
            dry_food_servings = random.uniform(globals.CHILD_MALE_DRY_FOOD_SERVINGS_MIN, globals.CHILD_FEMALE_DRY_FOOD_SERVINGS_MAX)
            dairy_servings = random.uniform(globals.CHILD_MALE_DAIRY_SERVINGS_MIN, globals.CHILD_FEMALE_DAIRY_SERVINGS_MAX)
            meat_servings = random.uniform(globals.CHILD_MALE_MEAT_SERVINGS_MIN, globals.CHILD_FEMALE_MEAT_SERVINGS_MAX)
            snacks_servings = random.uniform(globals.CHILD_MALE_SNACKS_SERVINGS_MIN, globals.CHILD_FEMALE_SNACKS_SERVINGS_MAX)
            store_prepared_servings = random.uniform(globals.CHILD_MALE_STORE_PREPARED_SERVINGS_MIN, globals.CHILD_FEMALE_STORE_PREPARED_SERVINGS_MAX)
        else: #FEMALE
            veg_servings = random.uniform(globals.CHILD_MALE_VEG_SERVINGS_MIN, globals.CHILD_FEMALE_VEG_SERVINGS_MAX)
            dry_food_servings = random.uniform(globals.CHILD_MALE_DRY_FOOD_SERVINGS_MIN, globals.CHILD_FEMALE_DRY_FOOD_SERVINGS_MAX)
            dairy_servings = random.uniform(globals.CHILD_MALE_DAIRY_SERVINGS_MIN, globals.CHILD_FEMALE_DAIRY_SERVINGS_MAX)
            meat_servings = random.uniform(globals.CHILD_MALE_MEAT_SERVINGS_MIN, globals.CHILD_FEMALE_MEAT_SERVINGS_MAX)
            snacks_servings = random.uniform(globals.CHILD_MALE_SNACKS_SERVINGS_MIN, globals.CHILD_FEMALE_SNACKS_SERVINGS_MAX)
            store_prepared_servings = random.uniform(globals.CHILD_MALE_STORE_PREPARED_SERVINGS_MIN, globals.CHILD_FEMALE_STORE_PREPARED_SERVINGS_MAX)
        
        
        food_groups = FoodGroups.get_instance()
        self.req_servings:float = veg_servings + dry_food_servings + dairy_servings + meat_servings + snacks_servings + store_prepared_servings
        sum_pref = sum(self.fg_preference.values())
        self.req_servings_per_fg:dict[str,float] = dict()
        for item in food_groups.get_all_food_groups():  # type: ignore
            self.req_servings_per_fg.update({item:(self.req_servings/sum_pref)*self.fg_preference[item]})
        
        self.susceptibility:float = 0
        self.concern:list[float] = [random.uniform(globals.CHILD_CONCERN_MIN,globals.CHILD_CONCERN_MAX),random.uniform(globals.CHILD_CONCERN_MIN,globals.CHILD_CONCERN_MAX),1- random.uniform(globals.CHILD_CONCERN_MIN,globals.CHILD_CONCERN_MAX)]
        self.plate_waste_ratio:float = random.uniform(globals.CHILD_PLATE_WASTE_MIN, globals.CHILD_PLATE_WASTE_MAX)
        