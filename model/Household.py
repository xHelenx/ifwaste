
import collections
import random
import logging
from Child import Child
from Storage import Storage
import globals
from Adult import Adult
from Grid import Grid
from Location import Location
from DataLogger import DataLogger
from Person import Person
from FoodGroups import FoodGroups
from HouseholdCookingManager import HouseholdCookingManager
from HouseholdShoppingManager import HouseholdShoppingManager

class Household(Location):
    def __init__(self, id: int, grid:Grid,  datalogger:DataLogger) -> None:
        """Initializes a household

        Args:
            id (int): unique id of the household
            
        Class Variables: 
            pantry (Storage) : Storage for all unprepared items 
            fridge (Storage) : Storage for all prepared and preprepared items
            datalogger (DataLogger): datalogger for writing data files
            amount_children (int): Number of children in the house 
            amount_adults (int): Number of adults in the house 
            ppl (list[Person]): list of all members of the household
            household_concern (float, 0-1): aggregated level of concern of the household regarding avoidable waste during cooking and consumption
            req_servings_per_fg (list(float)): aggregated requiredment of servings of each food group of the entire household
            req_servings (float): required total servings aggregated over people and food groups
            hh_preference (dict[str,float]): aggregated preference list of each food group
            shopping_frequency (int, 1-7): amount of times the family goes for a normal shopping trip in a week
            budget (float): generally available budget within one pay day range
            log_shopping_time (float) : time spent shopping today
            log_cooking_time (float) : time spent cooking today
            shoppingManager (HouseholdShoppingManager): object that manages everything regarding the shopping process
            cookingManager (HouseholdCookingManager): object that manages everything regarding the cooking process
            
        """        
        super().__init__(id, grid, "HH_"+ str(id))
        self.pantry: Storage  = Storage()
        self.fridge: Storage = Storage()
        self.datalogger: DataLogger = datalogger
        ###HOUSEHOLD MEMBER
        self.amount_adults: int = globals.HH_AMOUNT_ADULTS #(if 1-person household is possible, set suscepti. to 0)
        self.amount_children: int = globals.HH_AMOUNT_CHILDREN
        self.adult_influence: float = 0.75 #not used atm
        self.child_influence: float = 1 - self.adult_influence #not used atm
        self.ppl: list = self.gen_ppl()
        self.household_concern: float = self.calculate_household_concern()
        
        ### HOUSEHOLD FOOD DEMAND
        self.req_servings_per_fg = collections.Counter()
        
        ppl_serving_lists = [person.req_servings_per_fg for person in self.ppl]
        for d in ppl_serving_lists:
            self.req_servings_per_fg.update(d)
        
        self.req_servings = sum(self.req_servings_per_fg.values())
        
        self.hh_preference: dict[str, float] = {fg: sum(person.fg_preference[fg] for person in self.ppl) / len(self.ppl) for fg in FoodGroups.get_instance().get_all_food_groups()}
        todays_time: list = [random.random()*globals.HH_MAX_AVAIL_TIME_PER_DAY for i in range(7)]  
        
        self.shopping_frequency:int = globals.HH_SHOPPING_FREQUENCY
        self.budget:float = globals.HH_DAILY_BUDGET * globals.HH_PAY_DAY_INTERVAL
        
        self.log_shopping_time: float = 0
        self.log_cooking_time: float = 0
        
        self.shoppingManager:HouseholdShoppingManager = HouseholdShoppingManager(
            budget = self.budget,
            pantry = self.pantry,
            fridge = self.fridge,
            req_servings_per_fg=self.req_servings_per_fg,
            grid=self.grid, 
            household=self,
            shopping_freq=self.shopping_frequency,
            time = todays_time,
            datalogger = self.datalogger,
            id = self.id,
            logger = self.logger
        )
        
        numerator = 0
        for person in self.ppl: 
            individual_waste_serv = person.plate_waste_ratio*person.req_servings
            numerator += individual_waste_serv
        household_plate_waste_ratio:float = numerator/self.req_servings
        
        self.cookingManager:HouseholdCookingManager = HouseholdCookingManager(
            pantry = self.pantry, 
            fridge = self.fridge,
            shoppingManager = self.shoppingManager, 
            datalogger = self.datalogger, 
            household_concern = self.household_concern,
            preference_vector = self.hh_preference,
            household_plate_waste_ratio = household_plate_waste_ratio,
            time = todays_time, 
            id = self.id,
            req_servings=self.req_servings,
            logger = self.logger
        )
        
    def _reset_logs(self) -> None: 
        """Resets logs after information has been written to datalogger
        """        
        self.log_shopping_time: float = 0
        self.log_cooking_time: float = 0

    def gen_ppl(self) -> list[Person]:
        """Generates the people living together in a household.

        Returns:
            ppl: list of member of the household
        """  
        ppl = []
        for _ in range(self.amount_adults):
            ppl += [Adult()]
        for _ in range(self.amount_children):
            ppl += [Child()]
        
        return ppl        
    
    def calculate_household_concern(self) -> float: 
        """Calculates the current average concern of the household 

        Returns:
            H_c: normalized level of concern of the entire household
        """        
        C_fam = []
        for person in self.ppl:
            influencing_concern = [0] * len(self.ppl[0].concern) #how important are other peoples opinion
            concern_of_person = [] #persons final concern level 
            children_num = self.amount_children
            adult_num = self.amount_adults
            if person.is_adult: 
                adult_num -= 1
            else: 
                children_num -=1
            for p in self.ppl:
                if p == person:
                    continue 
                influence = 0
                if p.is_adult:
                    influence = self.adult_influence/adult_num
                else:
                    influence = self.child_influence/children_num
                ps_concern = [influence * p.concern[i] for i in range(len(p.concern))]
                for i in range(len(influencing_concern)): 
                    influencing_concern[i] += ps_concern[i]
            for i in range(len(person.concern)):
                concern_of_person += [(1-person.susceptibility)*person.concern[i] + \
                person.susceptibility * influencing_concern[i]]
            C_fam += [concern_of_person]
        return sum([sum(x) for x in C_fam])/len(self.ppl[0].concern*(self.amount_adults+self.amount_children))
    
    
    def do_a_day(self) -> None:
        """Incapsulates a day of eating in the household. This consists 
        of one or multiple of the following: shopping groceries, preparing a meal 
        (quick of full cooking procedure), eating a meal, food decaying + throwing out food

        Return:
            
        """  
        
        self._reset_logs()      
        globals.log(self,globals.LOG_TYPE_DAY_SEPARATOR,"###########################################")
        globals.log(self,globals.LOG_TYPE_DAY_SEPARATOR,"Day %i:", globals.DAY)
        globals.log(self,globals.LOG_TYPE_DAY_SEPARATOR,"###########################################")
        globals.log(self,globals.LOG_TYPE_TOTAL_SERV, "before:fridge + pantry hold: %s", self.fridge.get_total_servings() + self.pantry.get_total_servings())
        # check if it is payday
        if globals.DAY % globals.HH_PAY_DAY_INTERVAL == 0:  #pay day
            self.shoppingManager.todays_budget += self.budget
        #globals.log(self,"Budget: %f", self.budget)
        shopping_time = 0
        #check if it is time for a big grocery shop
        if globals.DAY % self.shopping_frequency == 0:
            shopping_time = self.shoppingManager.shop(is_quickshop=False)
            
            globals.log(self,globals.LOG_TYPE_TOTAL_SERV, "after shopping: fridge + pantry hold: %s", self.fridge.get_total_servings() + self.pantry.get_total_servings())
        #cook and eat
        cooking_time = 0 
        quick_shopping_time, cooking_time = self.cookingManager.cook_and_eat(used_time=shopping_time)
        shopping_time += quick_shopping_time
        #decay food and throw spoiled food out
        globals.log(self,globals.LOG_TYPE_TOTAL_SERV, "after eating:fridge + pantry hold: %s", self.fridge.get_total_servings() + self.pantry.get_total_servings())
        self.decay_food()
        self.throw_food_out()    
        
        self.log_shopping_time = shopping_time
        self.log_cooking_time = cooking_time
        globals.log(self,globals.LOG_TYPE_TOTAL_SERV, "after throw out:fridge + pantry hold: %s", self.fridge.get_total_servings() + self.pantry.get_total_servings())

    
    def decay_food(self) -> None:
        """Decays food in fridge and pantry by reducing the expiration dates 
        """    
        self.fridge.current_items["days_till_expiry"] -= 1
        self.pantry.current_items["days_till_expiry"] -= 1

                
    def throw_food_out(self) -> None:
        """Throws out all food, that expired
        """    
        for location in [self.fridge.current_items, self.pantry.current_items]:
            spoiled_food = location[location["days_till_expiry"] <= 0.0] #selected spoiled food to track it
            if len(spoiled_food) > 0:
                debug_spoiled = 0

                for i in spoiled_food.index: 
                    (edible,inedible) = self.cookingManager._split_waste_from_food(meal=spoiled_food.loc[i],waste_type=globals.FW_INEDIBLE)
                    edible["reason"] = globals.FW_SPOILED
                    self.datalogger.append_log(self.id, "log_wasted", edible)   
                    self.datalogger.append_log(self.id, "log_wasted", inedible)  
                    if edible is not None: 
                        debug_spoiled += edible["servings"] 
                    if inedible is not None: 
                        debug_spoiled += inedible["servings"]
                    
                location.drop(spoiled_food.index, inplace=True)  # remove expired 
                globals.log(self,globals.LOG_TYPE_TOTAL_SERV, "spoiled : %s", debug_spoiled)      
                