import random
import globals
from FoodGroups import FoodGroups
from Person import Person

class Adult(Person):
    def __init__(self) -> None:
        """
        initalizes Adult.
        
        Class variables:
        
        self.req_servings (float):  recommended servings per day
        self.req_servings_per_fg (float):  recommended servings per day per fg
        self.concern:list[float]:  level of concern 
        self.plate_waste_ratio:float:  % of plate waste
        
        """        
        super().__init__()  
        self.age:int = random.randint(globals.ADULT_AGE_MIN,globals.ADULT_AGE_MAX)
        self.is_adult:bool = True
        self.kcal:float = random.gauss(2000, 500) - 500*self.gender
        
        if self.gender == globals.MALE: 
            veg_servings = random.uniform(globals.ADULT_MALE_VEG_SERVINGS_MIN, globals.ADULT_FEMALE_VEG_SERVINGS_MAX)
            dry_food_servings = random.uniform(globals.ADULT_MALE_DRY_FOOD_SERVINGS_MIN, globals.ADULT_FEMALE_DRY_FOOD_SERVINGS_MAX)
            dairy_servings = random.uniform(globals.ADULT_MALE_DAIRY_SERVINGS_MIN, globals.ADULT_FEMALE_DAIRY_SERVINGS_MAX)
            meat_servings = random.uniform(globals.ADULT_MALE_MEAT_SERVINGS_MIN, globals.ADULT_FEMALE_MEAT_SERVINGS_MAX)
            snacks_servings = random.uniform(globals.ADULT_MALE_SNACKS_SERVINGS_MIN, globals.ADULT_FEMALE_SNACKS_SERVINGS_MAX)
            baked_servings = random.uniform(globals.ADULT_MALE_BAKED_SERVINGS_MIN, globals.ADULT_MALE_SNACKS_SERVINGS_MAX)
            store_prepared_servings = random.uniform(globals.ADULT_MALE_STORE_PREPARED_SERVINGS_MIN, globals.ADULT_FEMALE_STORE_PREPARED_SERVINGS_MAX)
        else: #FEMALE
            veg_servings = random.uniform(globals.ADULT_MALE_VEG_SERVINGS_MIN, globals.ADULT_FEMALE_VEG_SERVINGS_MAX)
            dry_food_servings = random.uniform(globals.ADULT_MALE_DRY_FOOD_SERVINGS_MIN, globals.ADULT_FEMALE_DRY_FOOD_SERVINGS_MAX)
            dairy_servings = random.uniform(globals.ADULT_MALE_DAIRY_SERVINGS_MIN, globals.ADULT_FEMALE_DAIRY_SERVINGS_MAX)
            meat_servings = random.uniform(globals.ADULT_MALE_MEAT_SERVINGS_MIN, globals.ADULT_FEMALE_MEAT_SERVINGS_MAX)
            snacks_servings = random.uniform(globals.ADULT_MALE_SNACKS_SERVINGS_MIN, globals.ADULT_FEMALE_SNACKS_SERVINGS_MAX)
            baked_servings = random.uniform(globals.ADULT_FEMALE_BAKED_SERVINGS_MIN, globals.ADULT_FEMALE_SNACKS_SERVINGS_MAX)
            store_prepared_servings = random.uniform(globals.ADULT_MALE_STORE_PREPARED_SERVINGS_MIN, globals.ADULT_FEMALE_STORE_PREPARED_SERVINGS_MAX)
            
        food_groups = FoodGroups.get_instance()
        self.req_servings:float = veg_servings + dry_food_servings + dairy_servings + meat_servings + snacks_servings + baked_servings + store_prepared_servings
        sum_pref = sum(self.fg_preference.values())
        self.req_servings_per_fg:dict = dict()
        for item in food_groups.get_all_food_groups():  # type: ignore
            self.req_servings_per_fg.update({item:(self.req_servings/sum_pref)*self.fg_preference[item]})
        
        self.susceptibility:float = 0
        self.concern:list[float] = [random.uniform(globals.ADULT_CONCERN_MIN,globals.ADULT_CONCERN_MAX),random.uniform(globals.ADULT_CONCERN_MIN,globals.ADULT_CONCERN_MAX),1- random.uniform(globals.ADULT_CONCERN_MIN,globals.ADULT_CONCERN_MAX)]
        self.plate_waste_ratio:float = globals.ADULT_PLATE_WASTE
        