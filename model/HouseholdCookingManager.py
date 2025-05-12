import logging
import random
from typing import Literal, Union

import globals_config as globals_config
from Storage import Storage
from HouseholdShoppingManager import HouseholdShoppingManager
import pandas as pd
from DataLogger import DataLogger


class HouseholdCookingManager: 
    
    def __init__(self, pantry:Storage, fridge:Storage, shoppingManager:HouseholdShoppingManager,
                datalogger:DataLogger, household_concern:float,  preference_vector:dict[str,float],
                household_plate_waste_ratio:float, time:list[float], id:int, req_servings:float, 
                logger:logging.Logger|None) -> None:
        """Initializes the HouseholdCookingManager

        Args:
            pantry (Storage): pantry of the household (unprepared food)
            fridge (Storage): fridge of the household (preprepared and prepared food)
            shoppingManager (HouseholdShoppingManager): shopping manager for quickshops
            datalogger (DataLogger): data logger 
            household_concern (float): aggregated level of concern impacting ingredients to cook with it and order of eating leftover
            preference_vector (dict[str,float]): maps the food groups to the level of preference (0-1)
            household_plate_waste_ratio (float): aggregated household plate waste ratio (0-1)
            time (list[float]): available time for each day of the week
            id (int): id of the household (for debug logging)
            req_servings (float): aggregated required serving of the household
            logger (logging.Logger | None): logger for debugging purposes
        """        
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
        """Returns whether the household has enough ingredients to match the required servings

        Returns:
            bool: has enough ingredients
        """        
        return self.pantry.get_total_servings() > self.todays_servings
    
    def _has_enough_time(self) -> bool:
        """Returns whether the household has enough time to cook a full meal

        Returns:
            bool: has enough time
        """        
        return self.todays_time < globals_config.get_parameter_value(globals_config.HH_MIN_TIME_TO_COOK,self.id)
    
    def _reset_logs(self) -> None: 
        """Resets variables tracking infos for data logger
        """        
        self.log_today_eef = 0
        self.log_today_cooked = 0
        self.log_today_leftovers = 0
        self.log_today_quickcook = 0
    
    def _cook(self,strategy:Literal["random","EEF"],is_quickcook:bool) ->  tuple[Union[pd.Series, None], float,float]:
        """Encapsulates the cooking process 

        Args:
            strategy (Literal[&quot;random&quot;,&quot;EEF&quot;]): strategy that is applied during the cooking process
            - random: random ingredient selection
            - EEF: earliest expiring food first
            is_quickcook (bool): indicates whether this is a quick cook (vs. a normal full cook)

        Returns:
            tuple[Union[pd.Series, None], float,float]: meal, shopping_time, cooking_time
            meal = the meal that has been cooked
            shopping_time = in case a quick shop was necessary, time spent shoppig, else = 0
            cooking_time = time spent cooking
        """        
        shopping_time = 0
        cooking_time = 0
        if not self._has_enough_ingredients(): 
            shopping_time = self.shoppingManager.shop(is_quickshop=True) #shopping time ignored cause its short and we quickcook
            self.todays_time -= shopping_time 
            
        if not self._has_enough_time():
            is_quickcook = True
        
        ingredients = self._get_ingredients(is_quickcook,strategy)
        
        prepped = []
        debug_total_inedible = 0
        for ingredient in ingredients: 
            (edible,inedible) = self._split_waste_from_food(ingredient, waste_type=globals_config.FW_INEDIBLE)
            prepped.append(edible)
            if not inedible is None:
                debug_total_inedible += inedible["servings"]
                self.datalogger.append_log(self.id, "log_wasted",inedible)
                
        globals_config.log(self,globals_config.LOG_TYPE_TOTAL_SERV, "inedible: %s", debug_total_inedible)        
        prepped = pd.DataFrame(prepped)
        
        meal = None 
        if not prepped.empty:
            meal = self._combine_to_meal(prepped)
        
        if not is_quickcook: 
            self.log_today_cooked = 1 
        else: 
            self.log_today_quickcook = 1
            
        ## TODO calc cooking time
        cooking_time = globals_config.get_parameter_value(globals_config.HH_MIN_TIME_TO_COOK,self.id)
        if is_quickcook: 
            cooking_time /=2
            
        return meal, shopping_time, cooking_time
    
    def _combine_to_meal(self,items:pd.DataFrame) -> pd.Series: 
        """Helper function: combines all food items (inedible parts removed) to a meal

        Args:
            items (pd.DataFrame): food items of the meal, inedible parts have to be removed beforehand

        Returns:
            pd.Series: resulting meal
        """        
        meal = pd.Series()
        for fg in globals_config.FOOD_GROUPS["type"].to_list():
            meal[fg] = items[fg].sum()
            
        meal["servings"] = items["servings"].sum()
        meal["days_till_expiry"] = random.randint(4,7)
        meal["status"] = globals_config.STATUS_PREPARED
        meal["price"] = items["price"].sum()
        meal["inedible_percentage"] = 0.0 #we just cut off the inedible parts of all items before combining the item
                
        return meal
        
    def _get_ingredients(self,is_quickcook:bool, strategy:Literal["random","EEF"]) -> list[pd.Series]: 
        """Selects required ingredients depending on the strategy (random, EEF) and whether the meal 
        will be quickcook

        Args:
            is_quickcook (bool): is a quick cook, impacting the number of ingredients of the meal
            strategy (Literal[&quot;random&quot;,&quot;EEF&quot;]): strategy impacting how 
            the food items are chosen (random = random selection, EEF = earliest expiration first, items
            are selected based on their expiration date)

        Returns:
            list[pd.Series]: list of selected food items
        """        
        #how much do we want to cook:
        planned_servings = self._choose_how_much_to_cook()
        ingredients = []
        
        #sample which foodgroups to cook with
        food_groups = []
        if is_quickcook:
            servings_per_fg = self.pantry.get_servings_per_fg()
            food_groups = servings_per_fg[servings_per_fg > 0].index.to_list()
            food_groups = random.sample(food_groups, 
                                        min(globals_config.get_parameter_value(globals_config.NH_COOK_FG_PER_QC,self.id), 
                                                                        len(food_groups)))
        
        while planned_servings > 0 and not self.pantry.is_empty(): 
            to_eat = self._get_ingredient(strategy=strategy, is_quickcook=is_quickcook,food_groups=food_groups)
            if len(to_eat) == 0: #we cannot find more items in the fg, so we stop early (a bit hungry)
                break
            planned_servings -= to_eat["servings"] * (1-to_eat["inedible_percentage"]) #TEST LOGIC
            ingredients.append(to_eat)
                
        return ingredients
                    
    def _get_ingredient(self, strategy:Literal["EEF","random"], is_quickcook:bool,food_groups:list=[]) -> pd.Series: 
        """Helper function of "get_ingredients", includes selecting a single item from the pantry.

        Args:
            is_quickcook (bool): is a quick cook, impacting the number of ingredients of the meal
            strategy (Literal[&quot;random&quot;,&quot;EEF&quot;]): strategy impacting how 
            the food items are chosen (random = random selection, EEF = earliest expiration first, items
            are selected based on their expiration date)
            food_groups: refers to the allowed food groups types, is only set if quick_cook. Is used to limit cooking 
            to a quick meal

        Raises:
            ValueError: Trying to select an item from an empty pantry

        Returns:
            pd.Series: individual food item that has been selected
        """        
        
        to_eat = pd.Series()
        item = self.pantry.get_item_by_strategy(strategy=strategy, preference_vector=self.preference_vector,food_groups=food_groups)#consider they only use unused ingredients and dont cook with leftovers here    
        if item is not None:
            servings = item["servings"]        
            if not is_quickcook and servings > globals_config.get_parameter_value(globals_config.NH_COOK_SERVINGS_PER_GRAB,self.id): 
                servings = globals_config.get_parameter_value(globals_config.NH_COOK_SERVINGS_PER_GRAB,self.id)
            (to_eat, to_pantry) = self._split(item, servings)
            if not to_pantry is None: 
                self.pantry.add(to_pantry)
        return to_eat

    def _choose_how_much_to_cook(self) -> float: 
        """Calculates the amount of servings that will be cooked. Generally 
        the household tries to cook at least enough food to satisfies the required_servings 
        (if enough food is in the pantry). However household can choose to cook more to have 
        food for other days. The produced servings can be up to required_servings * NH_COOK_MAX_SCALER_COOKING_AMOUNT

        Returns:
            float: number of servings to be cooked
        """        
        available = self.pantry.get_total_servings() 
        ratio_avail_req  = available/self.todays_servings 
        if ratio_avail_req > 1: 
            if ratio_avail_req > globals_config.get_parameter_value(globals_config.NH_COOK_MAX_SCALER_COOKING_AMOUNT,self.id): 
                ratio_avail_req = globals_config.get_parameter_value(globals_config.NH_COOK_MAX_SCALER_COOKING_AMOUNT,self.id)
        else: 
            ratio_avail_req = 1 
        
        planned = random.uniform(1,ratio_avail_req) * self.todays_servings +\
            self.household_plate_waste_ratio * self.todays_servings #eat enough so consider pw already
        #TODO or should we not do tihs
        return planned
    
    def cook_and_eat(self, used_time:float) -> tuple[float,float]: 
        """Method managing the cooking and eating process

        Args:
            used_time (float): time that has already been spent for shopping

        Returns:
            tuple[float,float]: [time spent shopping, time spent cooking] in min
        """        
        #globals.log(self,"------> COOKING")    
        cooking_time = 0
        shopping_time = 0
        self._reset_logs()
        self.todays_time = self.time[globals_config.DAY%7] - used_time
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
                    self._eat_meal(strategy=strategy)
                    
        if strategy != "random":
            self.log_today_eef = 1
            
        globals_config.log(self,globals_config.LOG_TYPE_TOTAL_SERV,"consumed today: %f", self.req_servings - self.todays_servings)    
        #globals.log(self,"req servings: %f", self.req_servings)    
                
                
                
        return shopping_time, cooking_time
        
    def _determine_strategy(self) -> Literal['EEFfridge', 'EEFpantry','random']: 
        """Helper function: Determines which strategy should be applied for selecting food/ingredients

        Returns:
            str: selected strategy
        """        
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
            if  ((earliest_fridge <= globals_config.get_parameter_value(
                globals_config.NH_COOK_EXPIRATION_THRESHOLD,self.id)) and (earliest_fridge <= earliest_pantry)) and \
            (not self.fridge.is_empty()):
                strategy = "EEFfridge"
            elif ((earliest_pantry <= globals_config.get_parameter_value(
                globals_config.NH_COOK_EXPIRATION_THRESHOLD,self.id)) and (earliest_pantry <= earliest_fridge)) and \
            (not self.pantry.is_empty()): 
                strategy = "EEFpantry"
        return strategy
        
    def _eat_meal(self,strategy:str|None = None, meal:pd.Series|None = None)  -> None:
        """Encapsulates the entire eating process, from eating a given meal and/or choosing leftovers from the fridge,
        to tracking the consumption of the meal + created waste

        Args:
            Either the strategy for selecting a meal or a meal has to be passed
            strategy (str | None, optional): Strategy for selecting a meal. Defaults to None.
            meal (pd.Series | None, optional): Meal to consume. Defaults to None.
        """        
        assert not (strategy == None and meal is None)
        assert not (strategy != None and meal is not None)   
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
        """Function that is called by _eat_meal to manage the food consumption part.
        Here the food is eaten and tracked, plate waste is calculated and tracked in data logger

        Args:
            meal (pd.Series): _description_
            needed_serv (float): _description_
        """        

        (to_eat, to_fridge) = self._split(meal=meal, servings=needed_serv)
        (consumed, plate_waste) = self._split_waste_from_food(meal=to_eat, waste_type=globals_config.FW_PLATE_WASTE)
        self.todays_servings -= consumed["servings"]
        if to_fridge is not None: 
            self.fridge.add(to_fridge)
        self.datalogger.append_log(self.id,"log_eaten",consumed)
        if plate_waste is not None:
            self.datalogger.append_log(self.id,"log_wasted",plate_waste)
            
        globals_config.log(self,globals_config.LOG_TYPE_TOTAL_SERV, "plate_waste: %s", plate_waste["servings"])      
        
    def _split_waste_from_food(self,meal:pd.Series, waste_type:str) -> tuple[pd.Series , Union[pd.Series, None]]:
        """Methods that facilitates splitting a specific waste type from a meal and then returns 
        both portions individually

        Args:
            meal (pd.Series): meal to take waste from
            waste_type (str): waste type to split, can be FW_PLATE_WASTE, FW_INEDIBLE, FW_SPOILED

        Returns:
            tuple[pd.Series , Union[pd.Series, None]]: meal to consume, waste
        """        
        consumed = meal.copy(deep=True)
        waste = meal.copy(deep=True)
        total_serv = 0
        for fg in globals_config.FOOD_GROUPS["type"].to_list(): 
            portion = 0
            if waste_type == globals_config.FW_INEDIBLE: 
                portion = globals_config.FOOD_GROUPS[globals_config.FOOD_GROUPS["type"] == fg]["inedible_percentage"].iloc[0]
            elif waste_type == globals_config.FW_PLATE_WASTE: 
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
        
        if waste_type == globals_config.FW_INEDIBLE: 
            waste["price"] = 0 
            consumed["price"] = meal["price"]
        elif waste_type ==  globals_config.FW_PLATE_WASTE or waste_type == globals_config.FW_SPOILED: 
            waste["price"] = (waste["servings"]/meal["servings"]) * meal["price"]
            consumed["price"] = (consumed["servings"]/meal["servings"]) * meal["price"]
        
        if waste["servings"] == 0:
            waste = None 
        
        return (consumed, waste)  
        
    def _split(self,meal:pd.Series,servings:float) -> tuple[pd.Series , Union[pd.Series, None]]: 
        """Helper function to split a specific amount of servings from a meal (take equal portions of each 
        food item)

        Args:
            meal (pd.Series): meal to split
            servings (float): number of servings to split from the meal

        Returns:
            tuple[pd.Series , Union[pd.Series, None]]: meal consisting of "servings" amount of servings (to_eat), rest of the meal (to_fridge)
        """        
        serv_to_eat = meal["servings"]
        
        to_fridge = meal.copy(deep=True)
        to_eat = meal.copy(deep=True)
        
        if meal["servings"] > servings: 
            serv_to_eat = servings
            
        to_eat["servings"] = serv_to_eat
        to_fridge["servings"] -= serv_to_eat
        
        fgs = globals_config.FOOD_GROUPS["type"].to_list()
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
        """Helper function for cook_and_eat() to manage eating and cooking. This is the first round food is 
        prepared and consumed.

        Args:
            strategy (_type_): strategy used for cooking a meal (EEF=earliest expiration first, random)

        Returns:
            tuple[float,float]: [shopping time, cooking time] in min
        """        
        shopping_time = cooking_time = 0
        if strategy == "EEFfridge": #eat from fridge cause it expires soon
            if not self.fridge.is_empty():
                #globals.log(self,"from fridge:")    
                self._eat_meal(strategy=strategy)
        else: #cook with EEF ingredients or random
            if strategy == "EEFpantry":
                strategy = "EEF"
            is_quickcook = not self._has_enough_time()
            meal,shopping_time,cooking_time = self._cook(strategy=strategy,is_quickcook=is_quickcook)
            if meal is not None:
                self._eat_meal(meal=meal)   
        return shopping_time, cooking_time