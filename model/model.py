# IF-WASTE Version 1a
#  Additions from GAK
#   Uncommented time and income in House object to limit food purchases and cooking activities
#   Deducted total Price of food from House budget
 

import random 
import copy
import pandas as pd

def ingredient_test(l:list):
    if len(l) == 0:
        raise Exception("Ingredient list shouldn't be empty")
class Store():
    def __init__(self):
        self.shelves = pd.DataFrame(columns= [
            'Type', 
            'Servings', 
            'Expiration Min.', 
            'Expiration Max.',
            'Price',
            'kg',
            'kcal_kg',
            'Inedible Parts'
            ])
        self.stock_shelves()
        self.inventory = []
    
    def stock_shelves(self):
        food_types = [
            "Meat & Fish", 
            "Dairy & Eggs", 
            "Fruits & Vegetables", 
            "Dry Foods & Baked Goods", 
            "Snacks, Condiments, Liquids, Oils, Grease, & Other", 
            'Store-Prepared Items' 
            ]
        for food_type in food_types:
            self.shelves = self.shelves._append(self.food_data(food_type=food_type, servings=6), ignore_index=True)
            self.shelves = self.shelves._append(self.food_data(food_type=food_type, servings=12), ignore_index=True)
            self.shelves = self.shelves._append(self.food_data(food_type=food_type, servings=20), ignore_index=True)

    def food_data(self, food_type: str, servings:int):
        ''' RGO - 
        Could make price smaller per kg for things with more 
        servings to improve accuracy to a real market'''
        inedible_parts = 0
        if food_type == 'Meat & Fish':
            exp_min = 4 # days 
            exp_max = 11 # days
            kg = 0.09*servings # assume 90g meat per serving
            price = 6*2.2*kg # assume $6/lb to total for kg
            kcal_kg = 2240 # assume 2240 kcal per kg of meat
            inedible_parts = 0.1
        elif food_type == 'Dairy & Eggs':
            exp_min = 7 # days 
            exp_max = 28 # days
            kg = 0.109*servings # assume 109g dairy&egg per serving
            price = 6*16/27*2.2*kg # assume $6/27oz to total for kg
            kcal_kg = 1810 # assume 1810 kcal per kg of dairy&eggs
            inedible_parts = 0.1
        elif food_type == 'Fruits & Vegetables':
            exp_min = 5 # days 
            exp_max = 15 # days
            kg = 0.116*servings # assume 116g f,v per serving
            price = 3.62*2.2*kg # assume $3.62/lb to total for kg
            kcal_kg = 790 # assume 790 kcal per kg of f,v
        elif food_type == 'Dry Foods & Baked Goods':
            exp_min = 7 # days 
            exp_max = 8*7 # days
            kg = 0.065*servings # assume 65g per serving
            price = 1.5*2.2*kg # assume $1.50/lb to total for kg
            kcal_kg = 3360 # assume 3360 kcal per kg
        elif food_type == 'Snacks, Condiments, Liquids, Oils, Grease, & Other':
            exp_min = 7 # days 
            exp_max = 8*7 # days
            kg = 0.095*servings # assume 95g per serving
            price = 3.3*2.2*kg # assume $3.30/lb to total for kg
            kcal_kg = 2790 # assume 2790 kcal per kg
        elif food_type == 'Store-Prepared Items':
            exp_min = 2 # days 
            exp_max = 7 # days
            kg = 0.095*servings # assume 95g per serving
            price = 0.33*16*2.2*kg # assume $0.33/oz to total for kg
            kcal_kg = 2790 # assume 2790 kcal per kg
        else:
            raise ValueError(f"{food_type}is not a listed Food Type")
        new_food = {
            'Type': food_type, 
            'Servings': servings, 
            'Expiration Min.': exp_min, 
            'Expiration Max.': exp_max,
            'Price': price,
            'kg': kg,
            'kcal_kg': kcal_kg,
            'Inedible Parts': inedible_parts
            }
        return new_food
class Person():
    def __init__(self):
        self.age = random.randint(18, 65)
        self.gender = random.randint(0, 1) #1 is female
        self.kcal = random.gauss(2000, 500) - 500*self.gender
    def old(self):
        self.age += 1
        if self.age <= 18:
            self.kcal += 50 + 10*self.gender
        elif self.age > 30 and self.age <= 40:
            self.kcal -= 50 + 10*self.gender
class Child(Person):
    def __init__(self, parent: Person):
        self.age = random.randint(1, 18)
        self.kcal = random.gauss(1200, 200) + self.age*50
        self.gender = random.randint(0,1) #1 is female
        self.parent = parent
class Food():
    def __init__(self, food_data:dict):
        self.type = food_data['Type']
        self.kg = food_data['kg']
        self.servings = food_data['Servings']
        self.exp = random.randint(food_data['Expiration Min.'], food_data['Expiration Max.'])
        self.price_kg = food_data['Price']/self.kg
        self.inedible_parts = food_data['Inedible Parts']
        self.frozen = False
        self.serving_size = self.kg/self.servings
        self.kcal_kg = food_data['kcal_kg']
        self.status = 'Un-prepped' if self.type != 'Store-Prepared Items' else 'Store-prepped'
    def decay(self):
        if self.frozen == False:
            self.exp -= 1
    def split(self, f_list: list, 
        to_list: list = None, 
        servings: int = None, 
        kcal: float = None):
        to_list = f_list if to_list == None else to_list
        if servings == None and kcal == None:
            raise ValueError('Must specify either servings or kcal')
        elif servings != None and kcal != None:
            raise ValueError('Must specify either servings or kcal, not both')
        elif servings != None:
            if servings > self.servings:
                servings = self.servings
            new_food = Food({
                'Type': self.type,
                'kg': servings*self.serving_size,
                'Expiration Min.': self.exp,
                'Expiration Max.': self.exp,
                'Price': self.price_kg*servings*self.serving_size,
                'Servings': servings,
                'kcal_kg': self.kcal_kg,
                'Inedible Parts': self.inedible_parts
            })
            self.kg -= new_food.kg
            self.servings -= new_food.servings
            to_list.append(new_food)
        elif kcal != None:
            if kcal > self.kcal_kg*self.kg:
                kcal = self.kcal_kg*self.kg
            new_food = Food({
                'Type': self.type,
                'kg': kcal/self.kcal_kg,
                'Expiration Min.': self.exp,
                'Expiration Max.': self.exp,
                'Price': self.price_kg*kcal/self.kcal_kg,
                'Servings': (kcal/self.kcal_kg)/self.serving_size,
                'kcal_kg': self.kcal_kg,
                'Inedible Parts': self.inedible_parts
            })
            self.kg -= new_food.kg
            self.servings -= new_food.servings
            to_list.append(new_food)
        if self.kg <= 0.001 or self.servings <= 0.001:
            f_list.remove(self)
    def throw(self):
        # return a list of wasted food
        return [self]
class CookedFood(Food):
    def __init__(self, ingredients:list):
        self.ingredients = ingredients
        self.type = 'Cooked, Prepped, Leftovers'
        self.servings = max([ingredient.servings for ingredient in self.ingredients])
        self.kg = 0
        price = 0
        kcal = 0
        self.frozen = False
        self.inedible_parts = 0
        self.exp = random.randint(4,7)
        for ingredient in ingredients:
            ingredient.status = 'Home-prepped'
            self.kg += ingredient.kg
            price += ingredient.price_kg*ingredient.kg
            kcal += ingredient.kcal_kg*ingredient.kg
        self.price_kg = price/self.kg
        self.kcal_kg = kcal/self.kg
        self.serving_size = self.kg/self.servings
        self.status = 'Home-prepped'
    def split(self, kcal: float, f_list: list, to_list: list = None ):
        # An issue from running I found was the if statement was > instead of >=
        # because we want it to just move the whole thing if they are equal
        ingredient_test(self.ingredients)
        new_ingredients = []
        if kcal >= self.kcal_kg*self.kg:
            kcal = self.kcal_kg*self.kg
            f_list.remove(self)
            to_list.append(self)
        else:
            # ratio to take the proper amount from each ingredient
            kcal_ratio = kcal/(self.kcal_kg*self.kg)
            for ingredient in self.ingredients:
                new_food = ingredient.split(kcal=ingredient.kcal_kg*ingredient.kg*kcal_ratio, f_list = self.ingredients, to_list= new_ingredients) # take the proper amount of each ingredient
            new_cfood = CookedFood(ingredients=new_ingredients)
            self.kg -= new_cfood.kg
            to_list.append(new_cfood)
    def throw(self):
        # return a list of wasted food
        waste_list = []
        for ingredient in self.ingredients:
            ingredient.exp = self.exp
            waste_list.append(ingredient)
        return waste_list
class Inedible():
    def __init__(self, food:Food):
        # creates a waste from the inedible parts of a food
        self.type = food.type
        self.kg = food.kg*food.inedible_parts
        self.servings = food.servings
        self.price_kg = food.price_kg
        self.kcal_kg = 0
        self.status = 'Inedible'
        self.exp = None
        # update the food
        food.kg -= self.kg
        food.serving_size *= (1-food.inedible_parts)
        food.kcal_kg /= (1-food.inedible_parts) # assume inedible parts have no calories
class House():
    def __init__(self, store: Store, id: int):
        self.ppl = self.gen_ppl()
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
    def gen_ppl(self):
        # currently not generating children
        ppl = []
        for i in range(random.randint(1, 5)):
            p = Person()
            ppl.append(p)
        return ppl
    def do_a_day(self, day: int):
        if day < 7:#Gets the day of week for estimating cooking time available below
            dayOfWeek = day 
        else: 
            dayOfWeek = day % 7
            
        if day % self.shopping_frequency == 0:
            self.shop()
        # If the Household's time is low (less than 1 hour, skip cooking) GAK Addition
        if self.time[dayOfWeek] > -1:
            self.cook()
        self.what_to_eat()
        self.decay_food()
        # Create day of week counter...
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
    def what_to_cook(self):
        # randomly pick 5 ingredients
        while len(self.pantry) < 5:  # If the pantry is near bare... then force a shopping expedition!
            self.shop()
        ingredients = []
        servings = random.randint(4, 7)
        for i in range(5):
            item = random.choice(self.pantry)
            item.split(servings=servings, f_list=self.pantry, to_list=ingredients)
        if len(ingredients)+1 < 5:
            raise Exception("No empty ingredients list")
        return ingredients
    def prep(self, food:Food):
            if food.inedible_parts > 0 : 
                scraps = Inedible(food=food)
                self.trash.append(scraps)
    def cook(self):
        ingredients = self.what_to_cook()
        for ingredient in ingredients:
            self.prep(ingredient)
        meal = CookedFood(ingredients=ingredients)
        self.fridge.append(meal)
    def what_to_eat(self):
        kcal = self.kcal
        for food in self.fridge:
            if kcal <= 0:
                break
            kcal -= self.eat(food, kcal)
    def eat(self, food: Food, kcal: float):
        if food.kcal_kg*food.kg > kcal:
            food.split(kcal=kcal, f_list=self.fridge, to_list=self.eaten)
            return kcal
        else:
            food.split(kcal=food.kcal_kg*food.kg, f_list=self.fridge, to_list=self.eaten)
            return food.kcal_kg*food.kg

class Neighborhood():
    def __init__(self, num_houses= 10):
        self.houses = []
        store = Store()
        for i in range(num_houses):
            self.houses.append(House(store=store, id = i))
        self.bought = pd.DataFrame(columns=[
            'House',
            'Day Bought',
            'Type',
            'kg',
            'Price',
            'Servings',
            'kcal',
            'Exp'
        ])
        self.eaten = pd.DataFrame(columns=[
            'House',
            'Day Eaten',
            'Type',
            'kg',
            'Price',
            'Servings',
            'kcal',
            'Exp'
        ])
        self.wasted = pd.DataFrame(columns=[
            'House',
            'Day Wasted',
            'Type',
            'kg',
            'Price',
            'Servings',
            'kcal',
            'Status'
        ])
        self.still_have = pd.DataFrame(columns=[
            'House',
            'Type',
            'kg',
            'Price',
            'Servings',
            'kcal',
            'Exp'
        ])
    def run(self, days= 365):
        for i in range(days):
            for house in self.houses:
                house.do_a_day(day=i)
                self.collect_data(house=house, day=i)
        for house in self.houses:
            self.get_storage(house=house)
    def collect_data(self, house: House, day: int):
        for food in house.bought:
            self.bought.loc[len(self.bought)] = {
                'House': house.id,
                'Day Bought': day,
                'Type': food.type,
                'kg': food.kg,
                'Price': food.price_kg*food.kg,
                'Servings': food.servings,
                'kcal':food.kcal_kg*food.kg,
                'Exp': food.exp
            }
            house.bought.remove(food)
        for food in house.eaten:
            self.eaten.loc[len(self.eaten)] = {
                'House': house.id,
                'Day Eaten': day,
                'Type': food.type,
                'kg': food.kg,
                'Price':food.price_kg*food.kg,
                'Servings': food.servings,
                'kcal': food.kcal_kg*food.kg,
                'Exp': food.exp
            }
            house.eaten.remove(food)
        for food in house.trash:
            self.wasted.loc[len(self.wasted)] = {
                'House': house.id,
                'Day Wasted':day,
                'Type': food.type,
                'kg': food.kg,
                'Price': food.price_kg*food.kg,
                'Servings': food.servings,
                'kcal': food.kcal_kg*food.kg,
                'Exp': food.exp,
                'Status': food.status
            }
            house.trash.remove(food)
    def get_storage(self, house: House):
        for food in house.fridge:
            self.still_have.loc[len(self.still_have)] = {
                'House': house.id,
                'Type': food.type,
                'kg': food.kg,
                'Price': food.price_kg*food.kg,
                'Servings': food.servings,
                'kcal': food.kcal_kg*food.kg,
                'Exp': food.exp,
                'Status': food.status
            }
            house.fridge.remove(food)
        for food in house.pantry:
            self.still_have.loc[len(self.still_have)] = {
                'House': house.id,
                'Type': food.type,
                'kg': food.kg,
                'Price': food.price_kg*food.kg,
                'Servings': food.servings,
                'kcal': food.kcal_kg*food.kg,
                'Exp': food.exp
            }
            house.pantry.remove(food)
    def data_to_csv(self):
        self.bought.to_csv('outputs/bought.csv')
        self.eaten.to_csv('outputs/eaten.csv')
        self.wasted.to_csv('outputs/wasted.csv')
        self.still_have.to_csv('outputs/still_have.csv')

neighborhood = Neighborhood(num_houses=10)
neighborhood.run(days=56)
neighborhood.data_to_csv()