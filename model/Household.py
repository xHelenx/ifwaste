
import collections
import random
import logging
import numpy as np
import pandas as pd

from CookedFood import CookedFood
from Child import Child
from Storage import Storage
import globals
from Adult import Adult
from Grid import Grid
from DealAssessor import DealAssessor
from BasketCurator import BasketCurator
from FoodGroups import FoodGroups

class Household():
    def __init__(self, id: int, grid:Grid, is_serving_based:bool = True):
        """Initializes a household

        Args:
            id (int): unique id of the household
        """        
        self.grid = grid  
        self.pantry = Storage()
        self.fridge = Storage()
        self.id = id
        self.day = 0
        
        ###HOUSEHOLD MEMBER
        logging.debug("HOUSE INFO")
        self.amount_adults = globals.HH_AMOUNT_ADULTS #(if 1-person household is possible, set suscepti. to 0)
        self.amount_children = globals.HH_AMOUNT_CHILDREN
        logging.debug("Amount of adults: %i, children: %i", self.amount_adults, self.amount_children)
        self.adult_influence = 0.75 
        self.child_influence = 1 - self.adult_influence
        self.ppl = self.gen_ppl()
        self.household_concern = self.calculate_household_concern()
        
        ### HOUSEHOLD FOOD DEMAND
        self.req_servings_per_fg = collections.Counter()
        ppl_serving_lists = [ppl.req_servings_per_fg for ppl in self.ppl]
        for d in ppl_serving_lists:
            self.req_servings_per_fg.update(d)
        self.req_servings = sum(self.req_servings_per_fg.values())
        self.req_servings_per_fg = self.req_servings_per_fg
        numerator = 0
        for person in self.ppl: 
            individual_waste_serv = person.plate_waste_ratio*person.req_servings
            numerator += individual_waste_serv
        self.household_plate_waste_ratio = numerator/self.req_servings
        self.kcal = sum([person.kcal for person in self.ppl])
        self.is_serving_based = is_serving_based #eat meals either based on servings or on kcal counter

        
        ### SHOPPING CHARACTERISTICS
        self.shopping_frequency = random.randint(2, 7)
        self.budget = random.randint(5, 15)*self.amount_adults * 30 # per month GAK Addition
        self.pay_day_interval = globals.NEIGHBORHOOD_PAY_DAY_INTERVAL     
        self.price_sens = random.uniform(0,1)
        self.brand_sens = random.uniform(0,1)
        self.brand_pref = {store:random.uniform(0,1) for store in globals.NEIGHBORHOOD_STORE_TYPES}
        self.quality_sens = random.uniform(0,1)
        self.availability_sens = random.uniform(0,1)
        self.deal_sens = random.uniform(0,1)
        self.planner = random.uniform(0,1)
        
        sum_sens = self.price_sens + self.brand_sens + self.quality_sens + self.availability_sens + self.deal_sens
        self.price_sens /= sum_sens
        self.brand_sens /= sum_sens
        self.quality_sens /= sum_sens
        self.availability_sens /= sum_sens
        self.deal_sens /= sum_sens
        self.maxTimeForCookingAndShopping = 3.0  # This will change and become a HH input
        self.time = [random.random()*self.maxTimeForCookingAndShopping, random.random()*self.maxTimeForCookingAndShopping, 
                     random.random()*self.maxTimeForCookingAndShopping, random.random()*self.maxTimeForCookingAndShopping,
                     random.random()*self.maxTimeForCookingAndShopping, random.random()*self.maxTimeForCookingAndShopping, 
                     random.random()*self.maxTimeForCookingAndShopping] 
        
        
        ### TRACKING CURRENT STATUS
        
        self.todays_time = [random.random()*self.maxTimeForCookingAndShopping, random.random()*self.maxTimeForCookingAndShopping,
                     random.random()*self.maxTimeForCookingAndShopping, random.random()*self.maxTimeForCookingAndShopping,
                     random.random()*self.maxTimeForCookingAndShopping, random.random()*self.maxTimeForCookingAndShopping,
                     random.random()*self.maxTimeForCookingAndShopping]
        self.todays_kcal = self.kcal
        self.todays_servings = self.req_servings
        self.todays_servings_fg = self.req_servings_per_fg
        self.todays_budget = 0     
        logging.debug("req. kcal: %f, req servings: %i lvl of concern: %f", self.kcal, self.todays_servings, self.household_concern)
        
        ### LOGGING 
        self.log_eaten = []
        self.log_wasted = []
        self.log_bought = []
              
        self.log_today_eef = 0
        self.log_today_cooked = 0
        self.log_today_leftovers = 0
        self.log_today_quickcook = 0
        
    def reset_logging_todays_choices(self): 
        """resets the logging variables tracking the meal preparation
        
        """        
        self.log_today_eef = 0
        self.log_today_cooked = 0
        self.log_today_leftovers = 0
        self.log_today_quickcook = 0
    def gen_ppl(self):
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
    
    def get_what_to_buy(self): ##assess what to buy
        
#        for item in self.req_servings
        required_servings = dict()
        required_servings.update((x, y*self.shopping_frequency) for x, y in self.req_servings_per_fg.items())
        required_servings = pd.Series(required_servings)
        fridge_content = pd.Series(self.fridge.get_servings_per_fg())
        pantry_content = pd.Series(self.pantry.get_servings_per_fg())
        
        return required_servings - (fridge_content + pantry_content)
        
        
    def get_budget_for_this_purchase(self): #estimate budget for current shopping tour
        days_till_payday = self.day % self.pay_day_interval
        if days_till_payday == 0: 
            days_till_payday = self.pay_day_interval
        
        if days_till_payday >= self.shopping_frequency: #we are staying within this months budget plans:
            if self.todays_budget == 0: #no money to buy anything
                return 0 
            req_servings_till_payday = (self.req_servings * days_till_payday) - (self.fridge.get_servings() + self.pantry.get_servings())
            price_per_serving = self.todays_budget/req_servings_till_payday
            return price_per_serving * (self.req_servings * self.shopping_frequency) * globals.HH_OVER_BUDGET_FACTOR
        
        else: #hh will receive new money, so the budget estimate has to consider it
            #TODO check this sceanrio
            req_servings_to_buy = (self.req_servings * self.shopping_frequency) - (self.fridge.get_servings() + self.pantry.get_servings())
            req_servings_daily = req_servings_to_buy/self.shopping_frequency

            budget_before_pd = self.todays_budget/(req_servings_daily * days_till_payday)
            left_days = self.shopping_frequency-days_till_payday
            budget_after_pdf = (self.todays_budget - budget_before_pd + self.budget)/(req_servings_daily * left_days + self.req_servings * (self.pay_day_interval-left_days))

            return (budget_before_pd + budget_after_pdf) * globals.HH_OVER_BUDGET_FACTOR
            
    
    def calculate_household_concern(self): 
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
                ps_concern = [influence * p.concern[i] for i in range(3)]
                for i in range(len(influencing_concern)): 
                    influencing_concern[i] += ps_concern[i]
            for i in range(3):
                concern_of_person += [(1-person.susceptibility)*person.concern[i] + \
                person.susceptibility * influencing_concern[i]]
            C_fam += [concern_of_person]
        return sum([sum(x) for x in C_fam])/len(self.ppl[0].concern*(self.amount_adults+self.amount_children))
           
    def do_a_day(self, day: int):
        """Incapsulates a day of eating in the household. This consists 
        of one or multiple of the following: shopping groceries, preparing a meal 
        (quick of full cooking procedure), eating a meal, food decaying + throwing out food

        Args:
            day (int): current day
        """        
        logging.debug("###########################################")
        logging.debug("###########################################")
        logging.debug("Day %i:", day)
        logging.debug("Pantry: \n" + self.pantry.debug_get_content())
        logging.debug("Fridge: \n" + self.fridge.debug_get_content())
        self.day = day
        
        ##setting up the variables for the day
        self.reset_logging_todays_choices()
        self.todays_kcal = self.kcal
        self.todays_servings = self.servings
        
        if self.day%7 == 0: 
            self.todays_time = self.time
        
        ##check if it is time for a big grocery shop
        if self.day % self.shopping_frequency == 0:
            self.shop(is_quickshop=False)
            
        # check if it is payself.day
        if self.day % self.pay_day_interval == 0: #pay day
            self.todays_budget += self.budget
        
        ##choose meal 
        self.log_today_eef = int(random.uniform(0,1) < self.household_concern)
        strategy = "random"
        is_quickcook = False
        has_enough_time = self.todays_time[day%7] < globals.MIN_TIME_TO_COOK
        has_enough_ingredients = self.pantry.get_total_servings() > self.servings
        if not self.is_serving_based:
            has_enough_ingredients = self.pantry.get_total_kcal() > self.kcal

        #EEF 
        if self.log_today_eef: 
            earliest_fridge = self.fridge.get_earliest_expiry_date() 
            earliest_pantry = self.pantry.get_earliest_expiry_date() 
            
            #sth from fridge expires first
            if (earliest_fridge <= globals.EXPIRATION_THRESHOLD) and (earliest_fridge <= earliest_pantry):
                if not self.fridge.is_empty():
                    self.eat_meal(strategy="EEF") #TODO maybe not enough intake?
                if self.is_more_food_needed():
                    logging.debug("Cook for missing %f kcal, %i servings", self.todays_kcal, self.todays_servings)
                    is_quickcook = True
                    if not self.pantry.is_empty(): 
                        meal = self.cook(is_quickcook=is_quickcook,strategy="random")
                        self.eat_meal(meal=meal)
            #sth from pantry expires first
            elif (earliest_pantry <= globals.EXPIRATION_THRESHOLD) and (earliest_pantry <= earliest_fridge):
                #now we do RANDOM but with EXPIRY PRIO 
                strategy = "EEF"
        
        #random cooking or parametrized through EEF
        if not self.log_today_eef:#random cooking 
            if has_enough_ingredients:
                is_quickcook = has_enough_time
                meal = self.cook(is_quickcook=is_quickcook, strategy=strategy)
                self.eat_meal(meal=meal) 
                if self.is_more_food_needed() and not self.fridge.is_empty():
                    self.eat_meal(strategy=strategy)
            else: #has not enough ingredients 
                self.shop(is_quickshop=True)
                #eat SPF or QC mit bought ingredients 
                if self.pantry.get_total_items() > 0:
                    is_quickcook = True
                    meal = self.cook(is_quickcook=is_quickcook, strategy=strategy)
                    self.eat_meal(meal=meal)
                    if self.is_more_food_needed() and not self.fridge.is_empty():
                        self.eat_meal(strategy=strategy)
            
        logging.debug("---> Missing servings: %f, missing kcal %f:", self.todays_servings, self.todays_kcal)
        self.log_today_cooked = int(not is_quickcook)
        self.log_today_quickcook = int(is_quickcook)
    
        #decay food and throw spoiled food out
        self.decay_food()
        self.throw_food_out()
        
    def is_more_food_needed(self): 
        if self.is_serving_based: 
            return self.todays_servings > 0
        else: #kcal based
            return self.todays_kcal > 0 
    
    def shop(self, is_quickshop=False):
        """Shops for groceries and stores them in the correct location in the house
        """    
        #TODO handle quickshop    
        servings_to_buy_fg = self.get_what_to_buy()
        if servings_to_buy_fg.sum() < 0: #we dont need to buy anything
            return 
            
        budget = self.get_budget_for_this_purchase()
        selected_stores = []
        
        is_planner = self.planner > random.uniform(0,1)
        relevant_fg = servings_to_buy_fg[servings_to_buy_fg> 0].index.tolist()
        
        selected_stores += (self.choose_a_store(is_planner, selected_stores, required_fgs=relevant_fg))
            
        #if planner add more stores if necessary because of missing fg
        if is_planner: #planner hh 
            avail_fgs = selected_stores[0].get_available_food_groups()
            relevant_fg = servings_to_buy_fg[servings_to_buy_fg> 0].index.tolist()
            left_fg = [i for i in relevant_fg if i not in avail_fgs]
            if len(left_fg) > 0: 
                store = self.choose_a_store(is_planner, selected_stores, required_fgs=left_fg[0])
                if store != None: 
                    selected_stores += (store)
               
        #create initial basket with groceries
        basketCurator = BasketCurator()
        (basket, missing_servings_fg) = basketCurator.create_basket(servings_to_buy_fg,selected_stores,budget)
        
        #feasibility test
        (in_budget, left_budget) = basketCurator.is_basket_in_budget(basket, budget)
        (has_all_req_fg, missing_fgs) = basketCurator.does_basket_cover_all_fg(missing_servings_fg)
        
        is_adjustment_needed = False
        if not in_budget or not has_all_req_fg: 
            #NO PLANNER
            if not is_planner: #consider adding another store to route
                ##BUDGET CHECK
                if random.uniform(0,1) > 0.5: #either adding stores or adjusting baskets
                    #adding a store from a lower tier (hopefully cheaper)
                    store = self.choose_a_store(is_planner, selected_stores, needs_lower_tier=True)
                    if store != None: 
                        selected_stores.append(store)
                        #redo entire basket now with a bonus store
                        (basket, missing_servings_fg) = basketCurator.create_basket(servings_to_buy_fg,selected_stores,budget)
                        (in_budget, left_budget) = basketCurator.is_basket_in_budget(basket, budget)
                        if not in_budget:
                            is_adjustment_needed = True
                    else:
                        is_adjustment_needed = True
                else:
                    is_adjustment_needed = True
                    
                ## NOPLANNER FG CHECK
                if not has_all_req_fg:
                    if not is_planner: #consider adding another store to route
                        ##BUDGET CHECK
                        if len(selected_stores) < 2 and random.uniform(0,1) > 0.5: #either adding stores or adjusting baskets
                            #adding a store from a lower tier
                            required_fg = missing_fgs[missing_fgs > 0].index.tolist()
                            store = self.choose_a_store(is_planner, selected_stores, required_fgs=required_fg)
                            if store != None: 
                                selected_stores.append(store)
                                #buy missing food items + keep old basket
                                (additional_basket, missing_servings_fg) = basketCurator.create_basket(missing_fgs,selected_stores,budget)
                                basket = pd.concat([basket, additional_basket], ignore_index=True) #merge baskets
                                #check feasibility
                                (in_budget, left_budget) = basketCurator.is_basket_in_budget(basket, budget)
                                (has_all_req_fg, missing_fgs) = basketCurator.does_basket_cover_all_fg(missing_servings_fg)
                                if not in_budget or not has_all_req_fg:
                                    is_adjustment_needed = True
                            else:
                                is_adjustment_needed = True
                        else:
                            is_adjustment_needed = True
            else: #is planner so no store adding, but will need adjustment
                is_adjustment_needed = True      
                  
        if is_adjustment_needed:
            #setup servings tracker (what is needed, what do we have, which fg covers for another one)
            rows = []
            for fg in FoodGroups._instance.get_all_food_groups():
                row = {'type': fg, 'required': servings_to_buy_fg[fg], 'got':servings_to_buy_fg[fg] - missing_servings_fg , 'is_in_other_fg': 0,
                        'is_replacing_other_fg': 0}
                rows += row
        
            servings_tracker = pd.DataFrame(rows)     
                
            basket = basketCurator.adjustBasket(basket, selected_stores, budget, servings_tracker)
            
                   
                    
        #calculated required time for shopping tour (final time for planner, current time for not planner)
        self.todays_time[self.day] -= self.grid.get_travel_time_entire_trip(self,selected_stores) 
        
        #get groceries
        #basket = self.get_groceries(is_quickshop)
        
        #put groceries away
        #for i in range(len(basket)):
        #    item_info = basket.iloc[i].to_dict()
        #    food = Food(item_info)
        #    logging.debug("Grocery: %f", food.kg)
        #    self.log_bought.append(copy.deepcopy(food))
        #    if food.type == globals.FGSTOREPREPARED:
        #        self.fridge.add(copy.deepcopy(food))
        #    else:
        #        self.pantry.add(copy.deepcopy(food))
    

           
        #check feasibility
        #start replacement strategy
        
        #checkout -> reduce stock
        #reduce budget
        #bring home, but in storage
        
        #if is_quickshop: 
        #    n_servings = self.servings 
        #    if random.uniform(0,1) > 0.5: #buy store prepared 
        #        basket = basket._append(self.store.buy_by_type(type=globals.FGSTOREPREPARED,servings=n_servings), ignore_index=True)
        #        basket = basket._append(self.store.buy_by_items(amount=random.randint(1,3)), ignore_index=True) #TODO could be store prepared again
        #    else: 
        #        basket = basket._append(self.store.buy_by_servings(servings=n_servings),ignore_index=True)
        #else:     
        #    basket = basket._append(self.store.buy_by_servings(servings=n_servings),ignore_index=True)
            
        #totalCost = basket['Price'].sum()
        #self.current_budget = self.current_budget - totalCost
        
      
    
    def choose_a_store(self,is_planner,selected_store:list, required_fgs=None, needs_lower_tier=None):
        assert not (required_fgs == None and needs_lower_tier == None)
        store_options = self.grid.get_stores_within_time_constraint(self,self.todays_time[self.day])
        #choose a store from possible options (not is_planner just selects 1 store here)
        if len(store_options) > 0: #TODO what if no store is within reach
            store_order = self.get_store_order(is_planner, required_fgs,store_options)
            selection = self._wheel_selection(store_order)
            while selection in selected_store: 
                if len(store_order) > 0: 
                    selection = self._wheel_selection(store_order)
                    store_order.remove(selection)
                else:
                    return None
        return selection
        
    def _wheel_selection(self, item:pd.Series, num_selections=1): 
        maxVal = item.sum()
        probabilities = item / maxVal
        cumulative_probabilities = probabilities.cumsum()
        
        indices = []
        for _ in range(num_selections):
            rand = np.random.random()
            selected_index = cumulative_probabilities[cumulative_probabilities >= rand].index[0]
            indices.append(selected_index)
        return indices
        
    def get_store_order(self, is_planner, relevant_fg,stores): 
        store_preference = pd.Series({store:0.0 for store in stores})
        
        if not is_planner: 
            for store in stores: #we only take 3 in account here, but as we do it everywhere its fine that it 
                #cant reach 1
                preference = (self.quality_sens * store.quality + self.price_sens * (1-store.price) +\
                    self.brand_sens * self.brand_pref[store.store_type.name])
                store_preference[store] = preference
        else: 
            dealAssessor = DealAssessor()
            best_deals = dealAssessor.assess_best_deals(stores)
            
            for store in stores: 
                local_deal = dealAssessor.assess_best_deals([store])
                #relevant_fg = servings_to_buy_fg[servings_to_buy_fg> 0].index.tolist()
                deal = dealAssessor.calculate_deal_value(relevant_fg, local_deal, best_deals)
                    
                avail_fg_value  = 0
                if relevant_fg != None: 
                    avail_fg = store.get_available_food_groups()   
                    avail_fg_value  = len(relevant_fg)/len(avail_fg)
                                                           
                preference = (self.quality_sens * store.quality + self.price_sens * (1-store.price) +\
                    self.brand_sens * self.brand_pref[store.store_type.name] + self.deal_sens *\
                        deal + self.availability_sens *avail_fg_value)
                store_preference[store] = preference
                
        return store_preference
            
    
        
            
        
    
    def decay_food(self):
        """Decays the food in the household
        """    
        for location in [self.fridge.current_items, self.pantry.current_items]:
            for food in location: 
                food.decay() 
                
    def throw_food_out(self):
        """Throws out all food, that expired
        """        
        for location in [self.fridge.current_items, self.pantry.current_items]:
            for food in location: 
                if food.exp <= 0: 
                    location.remove(food)
                    food.status = globals.FW_EXPIRED
                    self.log_wasted.append(food)
    
    def get_ingredients(self, is_quickcook, strategy): 
        """Chooses the ingredients to use for a meal. Takes into account the way the family is eating (servings based 
        kcal)

        Args:
            strategy (str, optional):Default:   "random" = choose random ingredients to cook wit
                                                "EEF"    = choose "Earliest Expiration First" 
            is_quickcook (boolean): decides how man ingredients to get 
            
            
        Returns:
            ingredients: list[Food] with chosen ingredients for the meal to cook 
        """    
        ingredients = []
        todays_requirements = self.todays_servings
        per_grab = globals.SERVINGS_PER_GRAB
        if not self.is_serving_based: 
            todays_requirements = self.todays_kcal
            per_grab = globals.KCAL_PER_GRAB

        #decide if and how much more to cook 
        available = self.pantry.get_total_servings() 
        if not self.is_serving_based: 
            available = self.pantry.get_total_kcal()
        ratio_avail_req  = available/todays_requirements 
        
        if ratio_avail_req > 1: 
            if ratio_avail_req > globals.MAX_SCALER_COOKING_AMOUNT: 
                ratio_avail_req = globals.MAX_SCALER_COOKING_AMOUNT
        else: 
            ratio_avail_req = 1 
            
            
        planned = random.uniform(1,ratio_avail_req) * todays_requirements
        missing = planned
    
        if self.is_serving_based: 
            logging.debug("Cook %i servings, using QC: %s", planned, is_quickcook)
        else: 
            logging.debug("Cook %i kcal, using QC: %s", planned, is_quickcook)
        
        grabbed = per_grab
        if not is_quickcook: 
            while missing > 0:
                item = self.pantry.get_item_by_strategy(strategy)
                if item != None:
                    if grabbed < per_grab: 
                        grabbed = missing
                    if self.is_serving_based:
                        (portioned_food, left_food) = item.split(servings=grabbed)
                    else: 
                        (portioned_food, left_food) = item.split(kcal=grabbed)
                        
                    ingredients.append(portioned_food)
                    self.pantry.add(left_food)
                    
                    if self.is_serving_based: 
                        missing -= ingredients[-1].servings
                    else: 
                        missing -= ingredients[-1].kcal_kg * ingredients[-1].kg
        else: #now we only want to use few ingredients, so we might use the entire thing (as long as it is not too much)
            used_ingredients = 0 
            while missing > 0 and used_ingredients <= globals.INGREDIENTS_PER_QUICKCOOK:         
                item = self.pantry.get_item_by_strategy(strategy)
                if item != None:
                    if self.is_serving_based:
                        if item.servings > missing: 
                            grabbed = item.servings
                        (portioned_food, left_food) = item.split(servings=grabbed)
                    else: 
                        if item.kcal_kg * item.kg > missing: 
                            grabbed = item.kcal_kg * item.kg
                        (portioned_food, left_food) = item.split(kcal=grabbed)
                        
                    ingredients.append(portioned_food)
                    self.pantry.add(left_food)
                    logging.debug("Cooking with: " + str(ingredients[-1]))
                    if self.is_serving_based: 
                        missing -= ingredients[-1].servings
                    else: 
                        missing -= ingredients[-1].kcal_kg * ingredients[-1].kg
                    used_ingredients += 1
                else: 
                    break #pantry is empty but we used at least one ingredient
        assert ingredients != []
        return ingredients
        
    def cook(self,is_quickcook:bool, strategy="random"): 
        """Cooking a meal consists of choosing the ingredients and preparing the meal.
        CookedFood will always be moved to the fridge before eating

        Args:
            strategy (str): strategy of choosing ingredients
        """      
                
        #logging.debug("Cook with " + str(amount_ingredients) + " ingredients")
        ingredients = self.get_ingredients(is_quickcook,strategy)
        
        prepared_ingredients = []
        for ingredient in ingredients:
            #split ingredients in scraps and consumable food
            (prepared_ingredient, scraps) = ingredient.split_waste_from_food(waste_type=globals.FW_INEDIBLE)
            prepared_ingredients.append(prepared_ingredient)
            if scraps != None:
                self.log_wasted.append(scraps)
        meal = CookedFood(ingredients=prepared_ingredients)
        
        #logging.debug("Scraps kg: %f", debug_scraps_weight)
        #logging.debug("Ingredients kg: %f", debug_weight)
        #logging.debug("scraps + ingredients kg: %f", debug_scraps_weight + debug_weight)
        #logging.debug("ingredients - scraps kg: %f", debug_weight - debug_scraps_weight)
        #logging.debug("Produced: %f", meal.kg)
        
        return meal 
        
    def eat_meal(self, strategy=None, meal=None): #what_to_eat
        """Eating a meal consists of first choosing a meal by a strategy and then 
        consuming it (calorie update). Plate waste is generated during the eating 
        process. 

        Args:
            strategy (str, optional): Strategy to choose a meal.Defaults to "EEF".
                - EEF = Earliest Expiration First 
                - random = First in First out 

        Returns:
            kcal (int): Still missing kcal 
        """        
        #while not self.fridge.is_empty() and self.is_more_food_needed(): 
        assert not (strategy == None and meal == None)
        assert not (strategy != None and meal != None)
        
        if meal == None: 
            meal = self.fridge.get_item_by_strategy(strategy) 
            self.log_today_leftovers = 1 #yes we ate leftovers today 
        assert meal != None 
        
        if self.is_serving_based: #food intake based on servings
            servings_to_eat = meal.servings
            if meal.servings > self.todays_servings: 
                servings_to_eat = self.todays_servings
            (portioned_food, left_food) = meal.split(servings=servings_to_eat)
            self.todays_servings -= servings_to_eat
            self.todays_kcal -= portioned_food.get_kcal()
                          
        else: #food intake based on kcal
            kcal_to_eat = meal.get_kcal()
            if kcal_to_eat > self.todays_kcal: 
                kcal_to_eat = self.todays_kcal
            
            (portioned_food, left_food) = meal.split(kcal=kcal_to_eat)
            self.todays_kcal -= kcal_to_eat
            self.todays_servings -= portioned_food.servings
               
        #eating part includes plate waste
        (consumed_food, plate_waste) = portioned_food.split_waste_from_food(waste_type=globals.FW_PLATE_WASTE, plate_waste_ratio=self.household_plate_waste_ratio)
        logging.debug("Eating: " + str(consumed_food))
        
        self.log_eaten.append(consumed_food)
        if plate_waste != None: 
            self.log_wasted.append(plate_waste)
            
        if left_food != None:
            if left_food.servings > 1: 
                self.fridge.add(left_food)
            else:
                left_food.status = globals.FW_PLATE_WASTE
                self.log_wasted.append(left_food)  
        #logging.debug("-------------------")