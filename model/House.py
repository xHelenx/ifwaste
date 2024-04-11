
import collections
import copy
import random
import logging

from Food import Food
from CookedFood import CookedFood
from Person import Person
from Store import Store
from Child import Child
from Storage import Storage
from globalValues import * 

class House():
    def __init__(self, id: int, is_serving_based:bool = True):
        """Initializes a household

        Args:
            id (int): unique id of the household
        """        
        logging.debug("HOUSE INFO")
        self.amount_adults = 2 #(if 1-person household is possible, set suscepti. to 0)
        self.amount_children = random.randint(1,3) 
        logging.debug("Amount of adults: %i, children: %i", self.amount_adults, self.amount_children)
        self.adult_influence = 0.75 
        self.child_influence = 0.25         
        self.ppl = self.gen_ppl()   
        self.household_concern = self.calculate_household_concern()          
        self.household_req_servings = collections.Counter()
        ppl_serving_lists = [ppl.req_servings for ppl in self.ppl]
        for d in ppl_serving_lists:
            self.household_req_servings.update(d)
        self.req_total_servings = sum(self.household_req_servings.values())
        
        numerator = 0
        for person in self.ppl: 
            individual_waste_serv = person.plate_waste_ratio*sum(person.req_servings.values())
            numerator += individual_waste_serv
        self.household_plate_waste_ratio = numerator/self.req_total_servings
        
        
        self.kcal = sum([person.kcal for person in self.ppl])
        self.pantry = Storage()
        self.fridge = Storage()
        self.shopping_frequency = random.randint(1, 7)
        self.store = None
        self.id = id
        self.maxTimeForCookingAndShopping = 3.0  # This will change and become a HH input
        self.time = [random.random()*self.maxTimeForCookingAndShopping, random.random()*self.maxTimeForCookingAndShopping, 
                     random.random()*self.maxTimeForCookingAndShopping, random.random()*self.maxTimeForCookingAndShopping,
                     random.random()*self.maxTimeForCookingAndShopping, random.random()*self.maxTimeForCookingAndShopping, 
                     random.random()*self.maxTimeForCookingAndShopping] #free time per day GAK Addition 
        self.budget = random.randint(5, 15)*self.amount_adults * 30 # per month GAK Addition
        self.current_budget = self.budget
        self.vegetarian = False # Flag for Vegetation GAK Addition
        self.is_serving_based = is_serving_based #eat meals either based on servings or on kcal counter
        
        self.todays_kcal = self.kcal
        self.servings = sum(self.household_req_servings.values())
        self.todays_servings = self.servings
        
        self.weekday = -1
        logging.debug("req. kcal: %f, req servings: %i lvl of concern: %f", self.kcal, self.todays_servings, self.household_concern)
        
        self.log_eaten = []
        self.log_wasted = []
        self.log_bought = []
              
        self.log_today_eef = 0
        self.log_today_cooked = 0
        self.log_today_leftovers = 0
        self.log_today_quickcook = 0
        
        
    def add_store(self,store:Store): 
        """relates a store to the household
        TODO: atm only 1 store possible 

        Args:
            store (Store): store the household buys groceries from
        """        
        self.store = store
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
            ppl += [Person()]
        for _ in range(self.amount_children):
            ppl += [Child()]
        
        return ppl
    
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
        
        self.reset_logging_todays_choices()
        self.todays_kcal = self.kcal
        self.todays_servings = self.servings
        
        self.weekday = day%7 
        if day % self.shopping_frequency == 0:
            self.shop()
            
        if day % 30 == 0: #pay day
            self.current_budget += self.budget
        
        
        self.log_today_eef = int(random.uniform(0,1) < self.household_concern)
        if self.log_today_eef == 1: #prio is to eat expiring food first
            logging.debug("Select expiring food")
        
            earliest_fridge = self.fridge.get_earliest_expiry_date() 
            earliest_pantry = self.pantry.get_earliest_expiry_date() 
            
            if (earliest_fridge <= EXPIRATION_THRESHOLD) and (earliest_fridge <= earliest_pantry): 
                logging.debug("Choose meal from fridge")
                if not self.fridge.is_empty():
                    self.eat_meal(strategy="EEF") #TODO maybe not enough intake?
                if self.is_more_food_needed():
                    logging.debug("Cook for missing %f kcal, %i servings", self.todays_kcal, self.todays_servings)
                    meal = self.cook(is_quickcook=True,strategy="random") 
                    self.eat_meal(meal=meal)
            elif (earliest_pantry <= EXPIRATION_THRESHOLD) and (earliest_pantry <= earliest_fridge):
                logging.debug("Choose meal from pantry")
                meal = self.cook(is_quickcook=self.time[self.weekday]<MIN_TIME_TO_COOK, strategy="EEF") 
                self.eat_meal(meal=meal)
                while self.is_more_food_needed() and not self.fridge.is_empty():
                    self.eat_meal(strategy="random") #TODO maybe not enough intake?!
            else: 
                logging.debug("Nothing expires, choose a random meal")
                self.have_a_random_meal()
                
        else: #eating a random meal 
            logging.debug("Select random food")
            self.have_a_random_meal()
            
        logging.debug("---> Missing servings: %f, missing kcal %f:", self.todays_servings, self.todays_kcal)
        self.decay_food()
        self.throw_food_out()
        
    def is_more_food_needed(self): 
        if self.is_serving_based: 
            return self.todays_servings > 0
        else: #kcal based
            return self.todays_kcal > 0 
    def have_a_random_meal(self): 
        """
        Either eats leftovers from the fridge, performs a quick or proper cooking
        for the day depending on the available time and content of the fridge
        """  
        meal = self.cook(is_quickcook=self.time[self.weekday] < MIN_TIME_TO_COOK, strategy="random")
        self.eat_meal(meal=meal) 
        if self.is_more_food_needed() and not self.fridge.is_empty():  
            self.eat_meal(strategy="random")
            
            
    def what_to_buy(self):
        """Picks randomly good to buy and deducts cost from budget

        Returns:
            basket [list]: List of items to buy
        """        
        # picks randomly currently
        n_items = SCALER_SHOPPING_AMOUNT*self.shopping_frequency
        basket = self.store.shelves.sample(n=n_items, replace=True)
        totalCost = basket['Price'].sum()
        self.current_budget = self.current_budget - totalCost
        return basket
    
    def shop(self):
        """Shops for groceries and stores them in the correct location in the house
        
        """        
        
        basket = self.what_to_buy()
        logging.debug("---------------------------------------------")
        logging.debug("Get groceries, %i things bought", len(basket))
        for i in range(len(basket)):
            item_info = basket.iloc[i].to_dict()
            food = Food(item_info)
            self.log_bought.append(copy.deepcopy(food))
            if food.type == 'Store-Prepared Items':
                self.fridge.add(food)
            else:
                self.pantry.add(food)
        logging.debug("---------------------------------------------")
        logging.debug("Pantry: \n" + self.pantry.debug_get_content())
        logging.debug("Pantry: total of %i items", len(self.pantry.current_items))
        logging.debug("Fridge: \n" + self.fridge.debug_get_content())
        logging.debug("Fridge: total of %i items", len(self.fridge.current_items))
        logging.debug("---------------------------------------------")
        
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
                    food.status = "Expired"
                    self.log_wasted.append(food)
    def get_ingredients(self,is_quickcook,strategy="random") -> list: 
        """Chooses the ingredients to use for a meal depending on the chosen strategy

        Args:
            strategy (str, optional):Default:   "random" = choose random ingredients to cook wit
                                                "EEF"    = choose "Earliest Expiration First" 
            
        Returns:
            ingredients: list[Food] with chosen ingredients for the meal to cook 
        """        

        ingredients = []
        planned_servings = random.randint(1,3) * self.todays_servings #TODO: cooking 1-3 times the currently (!!)
        missing_servings = planned_servings
        
        logging.debug("Cook %i servings, using QC: %s", planned_servings, is_quickcook)
        
        while len(self.pantry.current_items) < MIN_TILL_SHOP:  # If the pantry does not have enough different ingredients
            self.shop() 
        grabbed_servings = SERVINGS_PER_GRAB
        if not is_quickcook: 
            while missing_servings > 0:
                item = self.pantry.get_item_by_strategy(strategy)
                if item != None:
                    if missing_servings < SERVINGS_PER_GRAB: 
                        grabbed_servings = missing_servings
                    (portioned_food, left_food) = item.split(servings=grabbed_servings)
                    ingredients.append(portioned_food)
                    self.pantry.add(left_food)
                    logging.debug("Cooking with: " + str(ingredients[-1]))
                    missing_servings -= ingredients[-1].servings
                else: 
                    self.shop() #TODO: particular item is missing, for now get more food
        else: 
            missing_ingredients = INGREDIENTS_PER_QUICKCOOK
            while missing_servings > 0 and missing_ingredients > 0:         
                item = self.pantry.get_item_by_strategy(strategy)
                if item != None:
                    if missing_servings < SERVINGS_PER_GRAB: 
                        grabbed_servings = missing_servings
                    (portioned_food, left_food) = item.split(servings=grabbed_servings)
                    ingredients.append(portioned_food)
                    self.pantry.add(left_food)
                    logging.debug("Cooking with: " + str(ingredients[-1]))
                    missing_servings -= ingredients[-1].servings
                    missing_ingredients -= 1
                else: 
                    self.shop() #TODO: particular item is missing, for now get more food
        assert ingredients != []
        return ingredients
    def cook(self,is_quickcook:bool, strategy="random"): 
        """Cooking a meal consists of choosing the ingredients and preparing the meal.
        CookedFood will always be moved to the fridge before eating

        Args:
            strategy (str): strategy of choosing ingredients
        """      
                
        #logging.debug("Cook with " + str(amount_ingredients) + " ingredients")
        self.log_today_cooked = int(not is_quickcook)
        self.log_today_quickcook = int(is_quickcook)
        
        ingredients = self.get_ingredients(is_quickcook,strategy)
        prepared_ingredients = []
        for ingredient in ingredients:
            #split ingredients in scraps and consumable food
            (prepared_ingredient, scraps) = ingredient.split_waste_from_food(waste_type="Inedible")
            prepared_ingredients.append(prepared_ingredient)
            
            if scraps != None:
                self.log_wasted.append(scraps)
        meal = CookedFood(ingredients=prepared_ingredients)
        logging.debug("Produced: " + str(meal))
        
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
        (consumed_food, plate_waste) = portioned_food.split_waste_from_food(waste_type="Plate Waste", plate_waste_ratio=self.household_plate_waste_ratio)
        logging.debug("Eating: " + str(consumed_food))
        self.log_eaten.append(consumed_food)
        if plate_waste != None: 
            self.log_wasted.append(plate_waste)
        self.fridge.add(left_food)  
        
