
import copy
import random

from Food import Food
from CookedFood import CookedFood
from Inedible import Inedible
from Person import Person
from Store import Store
from Child import Child

MIN_TIME_TO_COOK = 0.8 #at least 30min to make a meal with 5 ingredients 
INGREDIENTS_FULL_COOK = 5
TIME_PER_INGREDIENT = 0.2 #for a quick cook you need this time per ingredient

class House():
    def __init__(self, store: Store, id: int):
        
        self.amount_adults = 2 #(if 1-person household is possible, set suscepti. to 0)
        self.amount_children = random.randint(1,3) 
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
        
        self.weekday = 0
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
      
    def get_expiring_food(self, location, minExpiration):
        use_up = []
        for item in location: 
            if item.exp < minExpiration:
                use_up += [item]
        return use_up
           
    def do_a_day(self, day: int):
        self.weekday = day%7 
        if day % self.shopping_frequency == 0:
            self.shop()
        
        req_kcal = self.kcal
        if random.uniform(0,1) < self.household_concern: #prio is to eat expiring food first
            print("EEF")
            use_up_fridge = []
            use_up_pantry = []
            minExpiration = 4             
            use_up_fridge = self.get_expiring_food(self.fridge, minExpiration)
            use_up_fridge.sort(key=lambda x: x.exp)
            use_up_pantry = self.get_expiring_food(self.pantry, minExpiration)
            use_up_pantry.sort(key=lambda x: x.exp)
            
            earliest_fridge = minExpiration +1 
            earliest_pantry = minExpiration +1 
            if len(use_up_fridge) > 0: 
                earliest_fridge = use_up_fridge[0].exp            
            if len(use_up_pantry) > 0: 
                earliest_pantry = use_up_pantry[0].exp
            print("fridge,EEF", earliest_fridge)
            print("pantry,EEF", earliest_pantry)
            if (earliest_fridge <= minExpiration) and (earliest_fridge <= earliest_pantry): 
                print("from fridge")
                req_kcal = self.eat_meal(req_kcal,"EEF") #eat leftovers from fridge
                if req_kcal > 0: 
                    print("and cooking")
                    self.cook("random") ##quick cook here!
                    req_kcal = self.eat_meal(req_kcal,"FIFO")
            elif (earliest_pantry <= minExpiration) and (earliest_pantry <= earliest_fridge):
                print("from pantry")
                self.cook("EEF") #long cook
                req_kcal = self.eat_meal(req_kcal,"FIFO")
            else: 
                print("cook as no expiration")
                self.have_a_random_meal()
        else: #eating a random meal 
            print("random")
            self.have_a_random_meal()
        print(req_kcal) 
        print("---------------")    
        
        
        self.decay_food()
    def have_a_random_meal(self): 
        if self.time[self.weekday] < MIN_TIME_TO_COOK: #if there is not enough time
                req_kcal = self.eat_meal(self.kcal,"FIFO") #eat leftovers
                if req_kcal > 0: 
                    self.cook("random") ##quick cook is missing kcal
        else: #enough time to cook 
            self.cook("random") 
            req_kcal = self.eat_meal(self.kcal, "FIFO") #will provide sufficient kcal
        print(req_kcal)
    def what_to_buy(self):
        # picks randomly currently
        basket = self.store.shelves.sample(n=2*self.shopping_frequency, replace=True)
        # Deduct the cost of the food from the budget GAK Addition
        totalCost = basket['Price'].sum()
        self.budget = self.budget - totalCost
        return basket
    def shop(self):
        basket = self.what_to_buy()
        for i in range(len(basket)):
            item_info = basket.iloc[i].to_dict()
            food = Food(item_info)
            self.bought.append(copy.deepcopy(food))
            if food.type == 'Store-Prepared Items':
                self.fridge.append(food)
            else:
                self.pantry.append(food)
    def decay_food(self):
        for food in self.fridge:
            food.exp -= 1
            if food.exp <= 0:
                self.throw_away(food)
        for food in self.pantry:
            food.exp -= 1
            if food.exp <= 0:
                self.throw_away(food)
    def throw_away(self, food:Food):
        if food in self.pantry:
            self.pantry.remove(food)
        if food in self.fridge:
            self.fridge.remove(food)
        self.trash.append(food)
    def get_ingredients(self,amount_ingredients,strategy="random"): #what_to_cook
        """Chooses the ingredients to use for a meal depending on the chosen strategy

        Args:
            strategy (str, optional):Default:   "random" = choose random ingredients to cook wit
                                                "EEF"    = choose "Earliest Expiration First" 
            
        Returns:
            ingredients: list[Food] with chosen ingredients for the meal to cook 
        """        
        # randomly pick 5 ingredients
        while len(self.pantry) < amount_ingredients:  # If the pantry is near bare... then force a shopping expedition!
            self.shop()
        ingredients = []
        servings = random.randint(4, 7) #TODO
        
        if strategy == "random":
            for _ in range(amount_ingredients):
                item = random.choice(self.pantry)
                item.split(servings=servings, f_list=self.pantry, to_list=ingredients)
        else: #EFF 
            for i in range(amount_ingredients): 
                self.pantry = sorted(self.pantry, key=lambda x: x.exp)
                self.pantry[i].split(servings=servings, f_list=self.pantry, to_list=ingredients)
        #if len(ingredients)+1 < 5:
        #    raise Exception("No empty ingredients list")
        return ingredients
    def prep(self, food:Food):
            if food.inedible_parts > 0 : 
                scraps = Inedible(food=food)
                self.trash.append(scraps)
    def cook(self, strategy="random"):
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
                
        print("cook with", amount_ingredients)
        ingredients = self.get_ingredients(amount_ingredients,strategy)
        for ingredient in ingredients:
            self.prep(ingredient)
        meal = CookedFood(ingredients=ingredients)
        self.fridge.append(meal)
        
    def eat_meal(self, req_kcal, strategy="FIFO"): #what_to_eat
        """Eating a meal consists of first choosing a meal by a strategy and then 
        consuming it (calorie update)

        Args:
            req_kcal (int): amount of required kcal
            strategy (str, optional): Strategy to choose a meal.Defaults to "FIFO".
                - EEF = Earliest Expiration First 
                - FIFO = First in First out 

        Returns:
            kcal (int): Still missing kcal 
        """        
        if strategy=="EEF": #order fridge by expiration date
            self.fridge.sort(key=lambda x: x.exp)
        
        for food in self.fridge:
            if req_kcal <= 0:
                break
            req_kcal -= self.consume(food, req_kcal)
            return req_kcal
            
    def consume(self, food: Food, kcal: float): #TODO change Food to cookedfood
        """Updates the kcal-count and the food in the fridge as well as the eaten food

        Args:
            food (Food): meal that gets eaten
            kcal (float): current req_kcal 

        Returns:
            kcal: kcal left to consume
        """        
        if food.kcal_kg*food.kg > kcal:
            food.split(kcal=kcal, f_list=self.fridge, to_list=self.eaten)
            return kcal
        else:
            food.split(kcal=food.kcal_kg*food.kg, f_list=self.fridge, to_list=self.eaten)
            return food.kcal_kg*food.kg