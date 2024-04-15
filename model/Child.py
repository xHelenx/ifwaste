import random
from Person import Person
import globals


class Child(Person):
    def __init__(self):
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
        self.age = random.randint(2, 18)
        self.is_adult = False 
        
        self.kcal = random.gauss(1200, 200) + self.age*50
        self.req_servings = dict()        
        if self.gender == globals.MALE: 
            veg_servings = random.uniform(1.8,2.2)
            dry_food_servings = random.uniform(5.1,8.7)
            dairy_servings = random.uniform(2,2.1)
            meat_servings = random.uniform(3,6)
            snacks_servings = 0
            store_prepared_servings = 0
        else: #FEMALE
            veg_servings = random.uniform(1.8,2)
            dry_food_servings = random.uniform(4.5,7)
            dairy_servings = random.uniform(1.7,1.95)
            meat_servings = random.uniform(3,4)
            snacks_servings = 0
            store_prepared_servings = 0
        
        
        self.req_servings.update({globals.FTVEGETABLE:veg_servings})
        self.req_servings.update({globals.FTDRYFOOD:dry_food_servings})
        self.req_servings.update({globals.FTDAIRY:dairy_servings})
        self.req_servings.update({globals.FTMEAT:meat_servings})
        self.req_servings.update({globals.FTSNACKS:snacks_servings})
        self.req_servings.update({globals.FTSTOREPREPARED:store_prepared_servings})
          
        
        self.susceptibility = 0
        self.concern = [random.uniform(globals.CHILD_CONCERN_MIN,globals.CHILD_CONCERN_MAX),random.uniform(globals.CHILD_CONCERN_MIN,globals.CHILD_CONCERN_MAX),random.uniform(globals.CHILD_CONCERN_MIN,globals.CHILD_CONCERN_MAX)]
        self.plate_waste_ratio = random.uniform(globals.CHILD_PLATE_WASTE_MIN,globals.CHILD_PLATE_WASTE_MAX)