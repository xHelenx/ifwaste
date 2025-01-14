import logging
import random
from typing import Literal, Union

import globals
from Storage import Storage
from HouseholdShoppingManager import HouseholdShoppingManager
import pandas as pd
from DataLogger import DataLogger
from FoodGroups import FoodGroups


class HouseholdCookingManager: 
    
    def __init__(self, pantry:Storage, fridge:Storage, shoppingManager:HouseholdShoppingManager,
                datalogger:DataLogger, household_concern:float,  preference_vector:dict[str,float],
                household_plate_waste_ratio:float, time:list[float], id:int, req_servings:float, 
                logger:logging.Logger|None) -> None:
        self.pantry:Storage = pantry
        self.fridge:Storage = fridge
        self.shoppingManager: HouseholdShoppingManager = shoppingManager
        self.datalogger:DataLogger = datalogger
        self.household_concern: float = household_concern
        self.preference_vector:dict[str,float] = preference_vector
        self.household_plate_waste_ratio = household_plate_waste_ratio
        self.id = id 
        self.logger:logging.Logger|None = logger
        
        self.time:list[float] = time
        self.req_servings = req_servings
        
        self.todays_time: float = 0
        self.todays_servings: float = req_servings
        self.today:int = 0
        
        self.log_today_eef: int
        self.log_today_cooked: int
        self.log_today_leftovers: int
        self.log_today_quickcook: int
        
        
    def _has_enough_ingredients(self) -> bool: 
        return self.pantry.get_total_servings() > self.todays_servings
    
    def _has_enough_time(self) -> bool:
        return self.todays_time < globals.HH_MIN_TIME_TO_COOK
    
    def _reset_logs(self) -> None: 
        self.log_today_eef = 0
        self.log_today_cooked = 0
        self.log_today_leftovers = 0
        self.log_today_quickcook = 0
    
    def _cook(self,strategy:Literal["random","EEF"],is_quickcook:bool) ->  tuple[Union[pd.Series, None], float,float]:
        shopping_time = 0
        cooking_time = 0
        if not self._has_enough_ingredients(): 
            shopping_time = self.shoppingManager.shop(is_quickshop=True) #shopping time ignored cause its short and we quickcook
            self.todays_time -= shopping_time 
            
        if not self._has_enough_time():
            is_quickcook = True
        
        ingredients = self._get_ingredients(is_quickcook,strategy)
        
        prepped = []
        for ingredient in ingredients: 
            (edible,inedible) = self._split_waste_from_food(ingredient, waste_type=globals.FW_INEDIBLE)
            prepped.append(edible)
            if not inedible is None:
                self.datalogger.append_log(self.id, "log_wasted",inedible)
        prepped = pd.DataFrame(prepped)
        
        meal = None 
        if not prepped.empty: #TODO undo    
            meal = self._combine_to_meal(prepped)
        
        if not is_quickcook: 
            self.log_today_cooked = 1 
        else: 
            self.log_today_quickcook = 1
            
        ## TODO calc cooking time
        cooking_time = globals.HH_MIN_TIME_TO_COOK
        if is_quickcook: 
            cooking_time /=2
            
        return meal, shopping_time, cooking_time
    
    def _combine_to_meal(self,items:pd.DataFrame) -> pd.Series: 
        meal = pd.Series()
        fgs = FoodGroups.get_instance()
        for fg in fgs.get_all_food_groups():
            meal[fg] = items[fg].sum()
            
        meal["servings"] = items["servings"].sum()
        meal["days_till_expiry"] = random.randint(4,7)
        meal["status"] = globals.STATUS_PREPARED
        meal["price"] = items["price"].sum()
        meal["inedible_percentage"] = 0.0 #we just cut off the inedible parts of all items before combining the item
                
        return meal
        
    def _get_ingredients(self,is_quickcook:bool, strategy:Literal["random","EEF"]) -> list[pd.Series]: 
        #how much do we want to cook:
        planned_servings = self._choose_how_much_to_cook()
        ingredients = []
        
        if not is_quickcook:
            while planned_servings > 0 and not self.pantry.is_empty(): 
                to_eat = self._get_ingredient(strategy=strategy, is_quickcook=is_quickcook)
                planned_servings -= to_eat["servings"] * (1-to_eat["inedible_percentage"]) #TEST LOGIC
                ingredients.append(to_eat)
        else: #quickcook
            used_ingredients = 0
            while planned_servings > 0 and used_ingredients <= globals.COOK_INGREDIENTS_PER_QC and not self.pantry.is_empty(): 
                to_eat = self._get_ingredient(strategy=strategy, is_quickcook=is_quickcook)
                used_ingredients += 1
                ingredients.append(to_eat)
                planned_servings -= to_eat["servings"] * (1-to_eat["inedible_percentage"])
                
        return ingredients
                    
    def _get_ingredient(self, strategy:Literal["EEF","random"], is_quickcook:bool) -> pd.Series: 
        
        to_eat = pd.Series()
        item = self.pantry.get_item_by_strategy(strategy=strategy, preference_vector=self.preference_vector)#consider they only use unused ingredients and dont cook with leftovers here    
        if not item is None:
            servings = item["servings"]
            
        
            if not is_quickcook and servings > globals.COOK_SERVINGS_PER_GRAB: 
                servings = globals.COOK_SERVINGS_PER_GRAB
            (to_eat, to_pantry) = self._split(item, servings)
            if not to_pantry is None: 
                self.pantry.add(to_pantry)
        else: 
            raise ValueError("Pantry is empty, so we cannot grab ingredients")
        return to_eat

    def _choose_how_much_to_cook(self) -> float: 
        available = self.pantry.get_total_servings() 
        ratio_avail_req  = available/self.todays_servings 
        if ratio_avail_req > 1: 
            if ratio_avail_req > globals.COOK_MAX_SCALER_COOKING_AMOUNT: 
                ratio_avail_req = globals.COOK_MAX_SCALER_COOKING_AMOUNT
        else: 
            ratio_avail_req = 1 
        
        planned = random.uniform(1,ratio_avail_req) * self.todays_servings +\
            self.household_plate_waste_ratio * self.todays_servings #eat enough so consider pw already
        #TODO or should we not do tihs
        return planned
    
    def cook_and_eat(self, used_time:float) -> tuple[float,float]: 
        #globals.log(self,"------> COOKING")    
        cooking_time = 0
        shopping_time = 0
        self._reset_logs()
        self.todays_time = self.time[globals.DAY%7] - used_time
        self.todays_servings = self.req_servings
        
        strategy = self._determine_strategy()
        #globals.log(self,"cooking strategy: %s", strategy)    
        
        #first round of eating
        shopping_time, cooking_time = self._prepare_by_strategy(strategy)
            
        #still hungry -> fe
        if self.todays_servings > 0: 
            if strategy == "EEFfridge":  #we only ate from fridge - so lets quickly cook
                meal,shopping_time,cooking_time = self._cook("EEF", is_quickcook = True)
                #globals.log(self,"quick cook more:")    
                if meal is not None: 
                    #globals.log(self,meal["servings"])
                    self._eat_meal(meal=meal)
            else: #we already cooked or quick cooked -> so eat left overs now
                if strategy == "EEFpantry": 
                    strategy = "EEF"
                if not self.fridge.is_empty(): #else we are just hungry
                    #globals.log(self,"eat leftovers:")    
                    self._eat_meal(strategy)
                    
        if strategy != "random":
            self.log_today_eef = 1
            
        #globals.log(self,"missing servings: %f", self.todays_servings)    
        #globals.log(self,"req servings: %f", self.req_servings)    
                
        return shopping_time, cooking_time
        
    def _determine_strategy(self) -> Literal['EEFfridge', 'EEFpantry','random']: 
        strategy = "random"      
        is_eef = (random.uniform(0,1) < self.household_concern)  
        #EEF 
        if is_eef: 
            earliest_fridge = self.fridge.get_earliest_expiry_date() 
            if pd.isna(earliest_fridge): 
                earliest_fridge = float("inf")
            earliest_pantry = self.pantry.get_earliest_expiry_date() 
            if pd.isna(earliest_pantry): 
                earliest_pantry = float("inf")
            
            #sth from fridge or pantry expires soon -> EEF
            if  ((earliest_fridge <= globals.COOK_EXPIRATION_THRESHOLD) and (earliest_fridge <= earliest_pantry)) and \
            (not self.fridge.is_empty()):
                strategy = "EEFfridge"
            elif ((earliest_pantry <= globals.COOK_EXPIRATION_THRESHOLD) and (earliest_pantry <= earliest_fridge)) and \
            (not self.pantry.is_empty()): 
                strategy = "EEFpantry"
        return strategy
        
    def _eat_meal(self,strategy:str|None = None, meal:pd.Series|None = None)  -> None:
        assert not (strategy == None and meal is None)
        assert not (strategy != None and meal is not None)   
                
        servings = 0
        if meal is not None: 
            servings = str(format(meal["servings"], ".2f"))
            #msg = "eat meal: " + str(strategy) + " servings: " + str(servings)
            #globals.log(self, msg)    
        needed_serv = self.todays_servings + self.household_plate_waste_ratio * self.todays_servings
        
        if meal is None and needed_serv > 0.001:  
            meal = self.fridge.get_item_by_strategy(strategy=strategy, preference_vector=self.preference_vector) # type: ignore
            while needed_serv > 0.001 and not meal is None: #float balance
                self._consume(meal,needed_serv)
                needed_serv = self.todays_servings + self.household_plate_waste_ratio * self.todays_servings
                if needed_serv > 0.001: 
                    meal = self.fridge.get_item_by_strategy(strategy=strategy, preference_vector=self.preference_vector) # type: ignore
                    
                self.log_today_leftovers = 1 # type: ignore #yes we ate leftovers today 
        else: 
            needed_serv = self._consume(meal,needed_serv) # type: ignore

        
    def _consume(self,meal:pd.Series,needed_serv:float) -> None: 

        (to_eat, to_fridge) = self._split(meal=meal, servings=needed_serv)
        (consumed, plate_waste) = self._split_waste_from_food(meal=to_eat, waste_type=globals.FW_PLATE_WASTE)
        self.todays_servings -= consumed["servings"]
        if to_fridge is not None: 
            #globals.log(self,"to fridge:")
            #globals.log(self, to_fridge)
            self.fridge.add(to_fridge)
        
        #globals.log(self,"CONSUMED:")
        #globals.log(self, consumed)
        self.datalogger.append_log(self.id,"log_eaten",consumed)
        if plate_waste is not None:
            #globals.log(self,"PLATE WASTE:") 
            #globals.log(self, plate_waste)
            self.datalogger.append_log(self.id,"log_wasted",plate_waste)
        
        
        
    
    def _split_waste_from_food(self,meal:pd.Series, waste_type:str) -> tuple[pd.Series , Union[pd.Series, None]]:
        fgs = FoodGroups.get_instance() # type: ignore
        consumed = meal.copy(deep=True)
        waste = meal.copy(deep=True)
        total_serv = 0
        for fg in fgs.get_all_food_groups(): 
            portion = 0
            if waste_type == globals.FW_INEDIBLE: 
                portion = fgs.food_groups.loc[ fgs.food_groups["type"] == fg,  "inedible_percentage"].values[0]
            elif waste_type == globals.FW_PLATE_WASTE: 
                portion = self.household_plate_waste_ratio

            else: #spoiled is all will be removed 
                portion = 1
                
            serv_this_fg = consumed[fg] - (consumed[fg] * portion)
            consumed[fg] = serv_this_fg
            waste[fg] = waste[fg] * portion
            total_serv += serv_this_fg
    
        consumed["servings"] = total_serv
        waste["servings"] -= total_serv
        waste["reason"] = waste_type
        
        if waste_type == globals.FW_INEDIBLE: 
            waste["price"] = 0 
            consumed["price"] = meal["price"]
        elif waste_type ==  globals.FW_PLATE_WASTE or waste_type == globals.FW_SPOILED: 
            waste["price"] = (waste["servings"]/meal["servings"]) * meal["price"]
            consumed["price"] = (consumed["servings"]/meal["servings"]) * meal["price"]
        
        if waste["servings"] == 0:
            waste = None 
            
        
        return (consumed, waste)  
        
    def _split(self,meal:pd.Series,servings:float) -> tuple[pd.Series , Union[pd.Series, None]]: 
        serv_to_eat = meal["servings"]
        
        to_fridge = meal.copy(deep=True)
        to_eat = meal.copy(deep=True)
        
        if meal["servings"] > servings: 
            serv_to_eat = servings
            
        to_eat["servings"] = serv_to_eat
        to_fridge["servings"] -= serv_to_eat
        
        fgs = FoodGroups.get_instance().get_all_food_groups() # type: ignore
        for fg in fgs: # type: ignore
            to_eat[fg] = serv_to_eat/meal["servings"] * to_eat[fg]
            to_fridge[fg] -= serv_to_eat/meal["servings"] * to_fridge[fg]
            
        if to_fridge["servings"] == 0: 
            to_fridge = None
        else: 
            to_fridge["price"] = (to_fridge["servings"]/meal["servings"]) * to_fridge["price"]
            
        to_eat["price"] = (to_eat["servings"]/meal["servings"]) * to_eat["price"]
        
            
        return (to_eat, to_fridge)
        
        
    def _prepare_by_strategy(self,strategy) -> tuple[float,float]:
        shopping_time = cooking_time = 0
        if strategy == "EEFfridge": #eat from fridge cause it expires soon
            if not self.fridge.is_empty():
                #globals.log(self,"from fridge:")    
                self._eat_meal(strategy)
        else: #cook with EEF ingredients or random
            if strategy == "EEFpantry":
                strategy = "EEF"
            is_quickcook = not self._has_enough_time()
            meal,shopping_time,cooking_time = self._cook(strategy=strategy,is_quickcook=is_quickcook)

            servings = 0
            if meal is not None: 
                servings = str(format(meal["servings"], ".2f"))
                
            #globals.log(self,"is quickcook %s, cooked: %s", str(is_quickcook), servings)
            #globals.log(self,meal)
            if meal is not None:
                self._eat_meal(meal=meal)   
        return shopping_time, cooking_time