import logging
import random

from Food import Food


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
        
        #debug_kcals = []
        for ingredient in ingredients:
            ingredient.status = 'Home-prepped'
            self.kg += ingredient.kg
            price += ingredient.price_kg*ingredient.kg
            kcal += ingredient.kcal_kg*ingredient.kg
            #debug_kcals += [int(ingredient.kcal_kg*ingredient.kg)]
        self.price_kg = price/self.kg
        self.kcal_kg = kcal/self.kg
        self.serving_size = self.kg/self.servings
        self.status = 'Home-prepped'
        #logging.debug("Servings: "+ str(self.servings) + " Kcals: " + str(debug_kcals)+ " Total: " + str(int(self.kcal_kg*self.kg)))
    def split(self, kcal: float, f_list: list, to_list: list = None ):
        # An issue from running I found was the if statement was > instead of >=
        # because we want it to just move the whole thing if they are equal
        if len(self.ingredients) == 0:
            raise Exception("Ingredient list shouldn't be empty")
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
   