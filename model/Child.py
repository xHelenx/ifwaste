import random
from Person import Person
import globals

class Child(Person):
    def __init__(self) -> None:
        """
        initalizes a child.
        
        Class variables:
        
        self.req_servings (float):  recommended servings per day
        self.req_servings_per_fg (float):  recommended servings per day per fg
        self.concern:list[float]:  level of concern 
        self.plate_waste_ratio:float:  % of plate waste
        
        """ 
        super().__init__()
        self.is_adult:bool = False 
        
        if self.gender == globals.MALE: 
            veg_servings = globals.CHILD_MALE_VEG_SERVINGS * (1-globals.CHILD_MALE_STORE_PREPARED_RATIO)
            dry_food_servings = globals.CHILD_MALE_DRY_FOOD_SERVINGS * (1-globals.CHILD_MALE_STORE_PREPARED_RATIO)
            dairy_servings = globals.CHILD_MALE_DAIRY_SERVINGS * (1-globals.CHILD_MALE_STORE_PREPARED_RATIO)
            meat_servings = globals.CHILD_MALE_MEAT_SERVINGS * (1-globals.CHILD_MALE_STORE_PREPARED_RATIO)
            snacks_servings = globals.CHILD_MALE_SNACKS_SERVINGS * (1-globals.CHILD_MALE_STORE_PREPARED_RATIO)
            baked_servings = globals.CHILD_MALE_BAKED_SERVINGS * (1-globals.CHILD_MALE_STORE_PREPARED_RATIO)
            servings:float = veg_servings + dry_food_servings + dairy_servings + meat_servings + snacks_servings + baked_servings
            store_prepared_servings = servings * globals.CHILD_MALE_STORE_PREPARED_RATIO
        else: #FEMALE
            veg_servings = globals.CHILD_FEMALE_VEG_SERVINGS * (1-globals.CHILD_FEMALE_STORE_PREPARED_RATIO)
            dry_food_servings = globals.CHILD_FEMALE_DRY_FOOD_SERVINGS * (1-globals.CHILD_FEMALE_STORE_PREPARED_RATIO)
            dairy_servings = globals.CHILD_FEMALE_DAIRY_SERVINGS * (1-globals.CHILD_FEMALE_STORE_PREPARED_RATIO)
            meat_servings = globals.CHILD_FEMALE_MEAT_SERVINGS * (1-globals.CHILD_FEMALE_STORE_PREPARED_RATIO)
            snacks_servings = globals.CHILD_FEMALE_SNACKS_SERVINGS * (1-globals.CHILD_FEMALE_STORE_PREPARED_RATIO)
            baked_servings = globals.CHILD_FEMALE_BAKED_SERVINGS * (1-globals.CHILD_FEMALE_STORE_PREPARED_RATIO)
            servings:float = veg_servings + dry_food_servings + dairy_servings + meat_servings + snacks_servings + baked_servings
            store_prepared_servings = servings * globals.CHILD_FEMALE_STORE_PREPARED_RATIO
            
        
        self.req_servings:float = veg_servings + dry_food_servings + dairy_servings + meat_servings + snacks_servings + baked_servings + store_prepared_servings
        sum_pref = sum(self.fg_preference.values())
        self.req_servings_per_fg:dict[str,float] = dict()
        for item in globals.FOOD_GROUPS["type"].to_list():  # type: ignore
            self.req_servings_per_fg.update({item:(self.req_servings/sum_pref)*self.fg_preference[item]})
        
        self.susceptibility:float = 0
        #self.concern:list[float] = [random.uniform(globals.CHILD_CONCERN_MIN,globals.CHILD_CONCERN_MAX),random.uniform(globals.CHILD_CONCERN_MIN,globals.CHILD_CONCERN_MAX),1- random.uniform(globals.CHILD_CONCERN_MIN,globals.CHILD_CONCERN_MAX)]
        self.plate_waste_ratio:float = globals.CHILD_PLATE_WASTE
        