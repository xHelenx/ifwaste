
import copy
import random

from Food import Food
from CookedFood import CookedFood
from Inedible import Inedible
from Person import Person
from Store import Store


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