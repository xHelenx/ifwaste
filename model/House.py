
import copy
import random
import logging

from Food import Food
from CookedFood import CookedFood
from Inedible import Inedible
from Person import Person
from Store import Store
from Child import Child

MIN_TIME_TO_COOK = 0.8 #at least 30min to make a meal with 5 ingredients 
INGREDIENTS_FULL_COOK = 5
TIME_PER_INGREDIENT = 0.2 #for a quick cook you need this time per ingredient
EXPIRATION_THRESHOLD = 4

class House():
    def __init__(self, store: Store, id: int):
        """Initializes a household

        Args:
            store (Store): defines accessible store for the household
            id (int): unique id of the household
        """        
        self.amount_adults = 2 #(if 1-person household is possible, set suscepti. to 0)
        self.amount_children = random.randint(1,3) 
        self.servings = self.amount_adults + self.amount_children
        self.adult_influence = 0.75 
        self.child_influence = 0.25         
        
        self.ppl = self.gen_ppl()     
        self.household_concern = self.calculate_household_concern()    
        self.kcal = sum([person.kcal for person in self.ppl])
        self.pantry = []
        self.fridge = []
        self.eaten = []
        self.trash = []
        self.bought = []
        self.shopping_frequency = random.randint(1, 7)
        self.store = store
        self.id = id
        self.maxTimeForCookingAndShopping = 3.0  # This will change and become a HH input
        self.time = [random.random()*self.maxTimeForCookingAndShopping, random.random()*self.maxTimeForCookingAndShopping, 
                     random.random()*self.maxTimeForCookingAndShopping, random.random()*self.maxTimeForCookingAndShopping,
                     random.random()*self.maxTimeForCookingAndShopping, random.random()*self.maxTimeForCookingAndShopping, 
                     random.random()*self.maxTimeForCookingAndShopping] #free time per day GAK Addition 
        self.budget = random.randint(15, 50)*len(self.ppl) * 30 # per month GAK Addition
        self.vegetarian = False # Flag for Vegetation GAK Addition
        
        self.todays_kcal = self.kcal
        self.todays_servings = self.servings
        self.weekday = 0
        logging.debug("HOUSE INFO")
        logging.debug("req. kcal: %f, lvl of concern: %f", self.kcal, self.household_concern)
        
    def gen_ppl(self):
        """Generates the people living together in a household.

        Returns:
            ppl: list of member of the household
        """  
        ppl = []
        for _ in range(self.amount_adults):
            ppl += [Person(self.amount_adults)]
        for _ in range(self.amount_children):
            ppl += [Child(self.amount_children)]
        
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
      
    def get_expiring_food(self, location):
        """Returns the expiring food withing the EXPIRATION_THRESHOLD 
        from a location

        Args:
            location (list): Get food either from fridge or pantry

        Returns:
            list: list of food, that will expire within EXPIRATION_THRESHOLD
        """        
        use_up = []
        for item in location: 
            if item.exp <= EXPIRATION_THRESHOLD:
                use_up += [item]
        return use_up
           
    def do_a_day(self, day: int):
        """Incapsulates a day of eating in the household. This consists 
        of one or multiple of the following: shopping groceries, preparing a meal 
        (quick of full cooking procedure), eating a meal, food decaying + throwing out food

        Args:
            day (int): _description_
        """        
        logging.debug("###########################################")
        logging.debug("###########################################")
        logging.debug("Day %i:", day)
        logging.debug("Pantry: \n" + self.debug_get_content(self.pantry))
        logging.debug("Fridge: \n" + self.debug_get_content(self.fridge))
        
        self.todays_kcal = self.kcal
        self.todays_servings = self.servings
        
        self.weekday = day%7 
        if day % self.shopping_frequency == 0:
            self.shop()
        
        if random.uniform(0,1) < self.household_concern: #prio is to eat expiring food first
            logging.debug("Select expiring food")
            use_up_fridge = []
            use_up_pantry = []            
            use_up_fridge = self.get_expiring_food(self.fridge)
            use_up_fridge.sort(key=lambda x: x.exp)
            use_up_pantry = self.get_expiring_food(self.pantry)
            use_up_pantry.sort(key=lambda x: x.exp)
            
            earliest_fridge = EXPIRATION_THRESHOLD +1 
            earliest_pantry = EXPIRATION_THRESHOLD +1 
            if len(use_up_fridge) > 0: 
                earliest_fridge = use_up_fridge[0].exp            
            if len(use_up_pantry) > 0: 
                earliest_pantry = use_up_pantry[0].exp
            if (earliest_fridge <= EXPIRATION_THRESHOLD) and (earliest_fridge <= earliest_pantry): 
                logging.debug("Choose meal from fridge")
                self.eat_meal("EEF") #eat leftovers from fridge
                if self.todays_kcal > 0: 
                    logging.debug("Cook for missing %f kcal", self.todays_kcal)
                    self.cook("random") 
                    self.eat_meal("FIFO")
                    logging.debug("Missing kcal: " + str(self.todays_kcal))
            elif (earliest_pantry <= EXPIRATION_THRESHOLD) and (earliest_pantry <= earliest_fridge):
                logging.debug("Choose meal from pantry")
                self.cook("EEF") 
                self.eat_meal("FIFO")
                logging.debug("Missing kcal: " + str(self.todays_kcal))
            else: 
                logging.debug("Nothing expires, choose a random meal")
                self.have_a_random_meal()
                
        else: #eating a random meal 
            logging.debug("Select random food")
            self.have_a_random_meal()
        
        self.decay_food()
        self.throw_food_out()
    def have_a_random_meal(self): 
        """
        Either eats leftovers from the fridge, performs a quick or proper cooking
        for the day depending on the available time and content of the fridge
        """        
        if self.time[self.weekday] < MIN_TIME_TO_COOK: #if there is not enough time
                self.eat_meal("FIFO") #eat leftovers
                if self.todays_kcal > 0: 
                    self.cook("random") ##quick cook is missing kcal
                    self.eat_meal("FIFO") #eat leftovers
        else: #enough time to cook 
            self.cook("random")  
            self.eat_meal("FIFO") 
        logging.debug("Missing kcal: " + str(self.todays_kcal))
    def what_to_buy(self):
        """Picks randomly good to buy and deducts cost from budget

        Returns:
            basket [list]: List of items to buy
        """        
        # picks randomly currently
        basket = self.store.shelves.sample(n=2*self.shopping_frequency, replace=True)
        # Deduct the cost of the food from the budget GAK Addition
        totalCost = basket['Price'].sum()
        self.budget = self.budget - totalCost
        return basket
    def shop(self):
        """Shops for groceries and stores them in the correct location in the house
        
        """        
        logging.debug("---------------------------------------------")
        logging.debug("Get groceries")
        basket = self.what_to_buy()
        for i in range(len(basket)):
            item_info = basket.iloc[i].to_dict()
            food = Food(item_info)
            self.bought.append(copy.deepcopy(food))
            if food.type == 'Store-Prepared Items':
                self.fridge.append(food)
            else:
                self.pantry.append(food)
        logging.debug("---------------------------------------------")
        logging.debug("Pantry: \n" + self.debug_get_content(self.pantry))
        logging.debug("Fridge: \n" + self.debug_get_content(self.fridge))
        logging.debug("---------------------------------------------")
        
    def decay_food(self):
        """Decays the food in the household
        """    
        for location in [self.fridge, self.pantry]:
            for food in location: 
                food.decay() 
                
    def throw_food_out(self):
        """Throws out all food, that expired
        """        
        for location in [self.fridge, self.pantry]:
            for food in location: 
                if food.exp <= 0: 
                    location.remove(food)
                    self.trash.append(food)
    def get_ingredients(self,amount_ingredients,strategy="random") -> list: 
        """Chooses the ingredients to use for a meal depending on the chosen strategy

        Args:
            strategy (str, optional):Default:   "random" = choose random ingredients to cook wit
                                                "EEF"    = choose "Earliest Expiration First" 
            
        Returns:
            ingredients: list[Food] with chosen ingredients for the meal to cook 
        """        

        while len(self.pantry) < amount_ingredients:  # If the pantry does not have enough different ingredients
            self.shop()
        ingredients = []
        servings = random.randint(1,3) * self.servings #amount of servings that are cooked  
        
        logging.debug("Cook %i servings", servings)
        if strategy == "random":
            for i in range(amount_ingredients):
                item = random.choice(self.pantry)
                item.split(servings=servings, f_list=self.pantry, to_list=ingredients)
                logging.debug("Cooking with: " + str(ingredients[i]))
        else: #EFF 
            for i in range(amount_ingredients): 
                self.pantry = sorted(self.pantry, key=lambda x: x.exp)
                self.pantry[0].split(servings=servings, f_list=self.pantry, to_list=ingredients)
                logging.debug("Cooking with: " + str(ingredients[i]))
        return ingredients
    def prep(self, food:Food):
            if food.inedible_parts > 0 : 
                scraps = Inedible(food=food)
                self.trash.append(scraps)
    def cook(self, strategy="random"): ###!TODO: must lead to a meal, that suffices servings/kcal        
        """Cooking a meal consists of choosing the ingredients and preparing the meal.
        CookedFood will always be moved to the fridge before eating

        Args:
            strategy (str): strategy of choosing ingredients
        """      
        amount_ingredients = INGREDIENTS_FULL_COOK  
        if self.time[self.weekday] < MIN_TIME_TO_COOK:
            amount_ingredients = int(self.time[self.weekday]*TIME_PER_INGREDIENT)
            if amount_ingredients == 0: 
                amount_ingredients = 1
                
        logging.debug("Cook with " + str(amount_ingredients) + " ingredients")
        ingredients = self.get_ingredients(amount_ingredients,strategy)
        for ingredient in ingredients:
            self.prep(ingredient)
        meal = CookedFood(ingredients=ingredients)
        logging.debug("Produced: " + str(meal))
        self.fridge.append(meal)
        logging.debug("Fridge: \n" + self.debug_get_content(self.fridge))
        
        
    def eat_meal(self, strategy="FIFO"): #what_to_eat
        """Eating a meal consists of first choosing a meal by a strategy and then 
        consuming it (calorie update)

        Args:
            strategy (str, optional): Strategy to choose a meal.Defaults to "FIFO".
                - EEF = Earliest Expiration First 
                - FIFO = First in First out 

        Returns:
            kcal (int): Still missing kcal 
        """        
        if len(self.fridge) > 0:
            if strategy=="EEF": #order fridge by expiration date
                self.fridge.sort(key=lambda x: x.exp)
            
            while len(self.fridge) > 0 and self.todays_kcal > 0: 
                self.consume(self.fridge[0])
   
    def consume(self, food: Food): 
        """Updates the kcal-count and the food in the fridge as well as the eaten food

        Args:
            food (Food): meal that gets eaten

        Returns:
            kcal: kcal left to consume
        """        
        if food.kcal_kg*food.kg > self.todays_kcal:
            logging.debug("Eating: " + str(self.fridge[0]) + " --> " + str(int(self.todays_kcal)) + " kcal")
            food.split(kcal=self.todays_kcal, f_list=self.fridge, to_list=self.eaten)
            self.todays_kcal = 0
        else:
            logging.debug("Eating: " + str(self.fridge[0]))
            self.todays_kcal -= food.kcal_kg*food.kg #here!
            food.split(kcal=food.kcal_kg*food.kg, f_list=self.fridge, to_list=self.eaten)
    def debug_get_content(self, location) -> str: 
        """Debugging function to visualized the current content of a location (fridge, pantry)

        Args:
            location (list): Location to visualize content of

        Returns:
            str: string representing content of location
        """    
        sorted_location = sorted(location,key=lambda x: x.exp)
        debug_str = ""
        for content in sorted_location: 
            debug_str += str(content) + "\n"
        return debug_str   