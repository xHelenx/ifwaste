import random
from Person import Person
import globals_config as globals_config

class Child(Person):
    def __init__(self, hh_id:int) -> None:
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
        
        if self.gender == globals_config.MALE: 
            veg_servings = globals_config.get_parameter_value(globals_config.CHILD_MALE_VEG_SERVINGS,hh_id) * (1-globals_config.get_parameter_value(globals_config.CHILD_MALE_STORE_PREPARED_RATIO,hh_id))
            dry_food_servings = globals_config.get_parameter_value(globals_config.CHILD_MALE_DRY_FOOD_SERVINGS,hh_id) * (1-globals_config.get_parameter_value(globals_config.CHILD_MALE_STORE_PREPARED_RATIO,hh_id))
            dairy_servings = globals_config.get_parameter_value(globals_config.CHILD_MALE_DAIRY_SERVINGS,hh_id) * (1-globals_config.get_parameter_value(globals_config.CHILD_MALE_STORE_PREPARED_RATIO,hh_id))
            meat_servings = globals_config.get_parameter_value(globals_config.CHILD_MALE_MEAT_SERVINGS,hh_id) * (1-globals_config.get_parameter_value(globals_config.CHILD_MALE_STORE_PREPARED_RATIO,hh_id))
            snacks_servings = globals_config.get_parameter_value(globals_config.CHILD_MALE_SNACKS_SERVINGS,hh_id) * (1-globals_config.get_parameter_value(globals_config.CHILD_MALE_STORE_PREPARED_RATIO,hh_id))
            baked_servings = globals_config.get_parameter_value(globals_config.CHILD_MALE_BAKED_SERVINGS,hh_id) * (1-globals_config.get_parameter_value(globals_config.CHILD_MALE_STORE_PREPARED_RATIO,hh_id))
            servings:float = veg_servings + dry_food_servings + dairy_servings + meat_servings + snacks_servings + baked_servings
            store_prepared_servings = servings * globals_config.get_parameter_value(globals_config.CHILD_MALE_STORE_PREPARED_RATIO,hh_id)
        else: #FEMALE
            veg_servings = globals_config.get_parameter_value(globals_config.CHILD_FEMALE_VEG_SERVINGS,hh_id) * (1-globals_config.get_parameter_value(globals_config.CHILD_FEMALE_STORE_PREPARED_RATIO,hh_id))
            dry_food_servings = globals_config.get_parameter_value(globals_config.CHILD_FEMALE_DRY_FOOD_SERVINGS,hh_id) * (1-globals_config.get_parameter_value(globals_config.CHILD_FEMALE_STORE_PREPARED_RATIO,hh_id))
            dairy_servings = globals_config.get_parameter_value(globals_config.CHILD_FEMALE_DAIRY_SERVINGS,hh_id) * (1-globals_config.get_parameter_value(globals_config.CHILD_FEMALE_STORE_PREPARED_RATIO,hh_id))
            meat_servings = globals_config.get_parameter_value(globals_config.CHILD_FEMALE_MEAT_SERVINGS,hh_id) * (1-globals_config.get_parameter_value(globals_config.CHILD_FEMALE_STORE_PREPARED_RATIO,hh_id))
            snacks_servings = globals_config.get_parameter_value(globals_config.CHILD_FEMALE_SNACKS_SERVINGS,hh_id) * (1-globals_config.get_parameter_value(globals_config.CHILD_FEMALE_STORE_PREPARED_RATIO,hh_id))
            baked_servings = globals_config.get_parameter_value(globals_config.CHILD_FEMALE_BAKED_SERVINGS,hh_id) * (1-globals_config.get_parameter_value(globals_config.CHILD_FEMALE_STORE_PREPARED_RATIO,hh_id))
            servings:float = veg_servings + dry_food_servings + dairy_servings + meat_servings + snacks_servings + baked_servings
            store_prepared_servings = servings * globals_config.get_parameter_value(globals_config.CHILD_FEMALE_STORE_PREPARED_RATIO,hh_id)
            
        
        self.req_servings:float = veg_servings + dry_food_servings + dairy_servings + meat_servings + snacks_servings + baked_servings + store_prepared_servings
        sum_pref = sum(self.fg_preference.values())
        self.req_servings_per_fg:dict[str,float] = dict()
        for item in globals_config.FOOD_GROUPS["type"].to_list():  # type: ignore
            self.req_servings_per_fg.update({item:(self.req_servings/sum_pref)*self.fg_preference[item]})
        
        self.susceptibility:float = 0
        #self.concern:list[float] = [random.uniform(globals.CHILD_CONCERN_MIN,globals.CHILD_CONCERN_MAX),random.uniform(globals.CHILD_CONCERN_MIN,globals.CHILD_CONCERN_MAX),1- random.uniform(globals.CHILD_CONCERN_MIN,globals.CHILD_CONCERN_MAX)]
        self.plate_waste_ratio:float = globals_config.get_parameter_value(globals_config.CHILD_PLATE_WASTE,hh_id)
        