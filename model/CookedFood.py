
import functools
import logging
import random

from Food import Food
import pandas as pd 


class CookedFood(Food):
    def __init__(self, ingredients:list[Food]=None, cooked_food:'CookedFood'=None, kg:float=-1, servings:float=-1): 
        """Create a CookedFood based on a list of ingredients

        Args:
            ingredients (list[Food]): list of ingredients to prepare meal
        """     
        assert not (ingredients != None and cooked_food != None)
        assert not (ingredients == None and cooked_food == None)
        
        if ingredients != None: 
            assert len(ingredients) > 0, "Len(Ingredients) must be > 0"
            self.ingredients = ingredients
            self.type = 'Cooked, Prepped, Leftovers'
            self.servings = sum([ingredient.servings for ingredient in self.ingredients])
            
            ingredient_serving_sum = ingredients[0].servings_per_type
            for ingredient in ingredients[1:]:
                ingredient_serving_sum += ingredient.servings_per_type
                
            self.servings_per_type =  ingredient_serving_sum
            self.kg = 0
            self.frozen = False
            self.inedible_parts = 0
            self.exp = random.randint(4,7)
            
            price = 0
            kcal = 0
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
        
        else: #cooked_food is not none 
            assert kg != -1 and servings != -1 
            self.ingredients = cooked_food.ingredients
            self.type = cooked_food.type
            self.servings = servings
            self.kg = kg
            self.frozen = cooked_food.frozen
            self.inedible_parts = cooked_food.inedible_parts
            self.exp = cooked_food.exp
            self.price_kg = cooked_food.price_kg
            self.kcal_kg = cooked_food.kcal_kg
            self.serving_size = cooked_food.serving_size
            self.status = cooked_food.status

        
    def split(self, servings: int = None, kcal: float = None):
        """Splits the current meal into the portion as defined through the 
        amount of calories or servings

        Args:
            kcal (float): required calories
            f_list (list): current meal/ingredients list
            to_list (list, optional): Leftover part of the meal. Defaults to None.
        """        
        if servings == None and kcal == None:
            raise ValueError('Must specify either servings or kcal')
        elif servings != None and kcal != None:
            raise ValueError('Must specify either servings or kcal, not both')
        elif servings != None: ##Serving based
            if servings > self.servings: 
                servings = self.servings
            portioned_food = CookedFood(cooked_food=self,kg=servings*self.serving_size, servings=servings)
            self.kg =- portioned_food.kg 
            self.servings -= portioned_food.servings
            self.servings_per_type -= self.servings_per_type.apply(lambda x: (servings/self.servings_per_type.values.sum()) * x)
        else: #Kcal based 
            if kcal > self.kcal_kg * self.kg: 
                kcal = self.kcal_kg * self.kg
            portioned_food = CookedFood(cooked_food=self,kg=kcal/self.kcal_kg, servings=(kcal/self.kcal_kg)/self.serving_size)
            self.kg =- portioned_food.kg 
            self.servings -= portioned_food.servings
            self.servings_per_type -= self.servings_per_type.apply(lambda x: (servings/self.servings_per_type.values.sum()) * x) 
    
        if self.kg <= 0.001 or self.servings <= 0.001: 
            self = None 
        
        return (portioned_food, self)