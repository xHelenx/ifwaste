import numpy as np
import pandas as pd
import globals

class Store():
    def __init__(self):
        """Initializes a store consisting of shelves
        """    
        self.shelves = pd.DataFrame(columns= [
            'Type', 
            'Servings', 
            'Expiration Min.', 
            'Expiration Max.',
            'Price',
            'kg',
            'kcal_kg',
            'Inedible Parts',
            'ServingsPerType'
            ])

        food_types = [
            globals.FTMEAT,
            globals.FTDAIRY,
            globals.FTVEGETABLE,
            globals.FTDRYFOOD,
            globals.FTSNACKS,
            globals.FTSTOREPREPARED
            ]
        for food_type in food_types:
            for serving in globals.SERVING_SIZES: 
                self.shelves = self.shelves._append(self.food_data(food_type=food_type, servings=serving), ignore_index=True)
        
    def buy_by_type(self, type, servings): 
        basket = pd.DataFrame()
        relevant_items = self.shelves[self.shelves["Type"] == type]
        while servings > 0: 
            item = relevant_items.sample(1,replace=True)
            basket = basket._append(item, ignore_index=True)
            servings -= item.Servings.values[0]
        return basket
        
    def buy_by_items(self, amount): 
        return self.shelves.sample(amount,replace=True)
        
    def buy_by_servings(self, servings): 
        basket = pd.DataFrame()
        while servings > 0: 
            item = self.shelves.sample(1,replace=True)
            basket = basket._append(item, ignore_index=True)
            servings -= item.Servings.values[0]
        return basket
        
    def food_data(self, food_type: str, servings:int) -> dict:
        """Creates a dictionary of a food to define its parameters

        Args:
            food_type (str): Food types
            servings (int): amount of servings to adjust the values to

        Returns:
            food_data dict: food information
        """        
        ''' TODO: RGO - 
        Could make price smaller per kg for things with more 
        servings to improve accuracy to a real market'''
        inedible_parts = 0
        
        zero_array = np.zeros(shape=(1,globals.TOTAL_FOOD_TYPES))
        servings_per_type = pd.DataFrame(zero_array, columns= [
            globals.FTMEAT,
            globals.FTDAIRY,
            globals.FTVEGETABLE,
            globals.FTDRYFOOD,
            globals.FTSNACKS,
            globals.FTSTOREPREPARED
            ])
        servings_per_type[food_type] = servings 
        assert servings_per_type.values.sum() > 0
        if food_type == globals.FTMEAT:
            exp_min = 4 # days 
            exp_max = 11 # days
            kg = 0.09*servings # assume 90g meat per serving
            price = 6*2.2*kg # assume $6/lb to total for kg
            kcal_kg = 2240 # assume 2240 kcal per kg of meat
            inedible_parts = 0.1 #%
        elif food_type == globals.FTDAIRY:
            exp_min = 7 # days 
            exp_max = 28 # days
            kg = 0.109*servings # assume 109g dairy&egg per serving
            price = 6*16/27*2.2*kg # assume $6/27oz to total for kg
            kcal_kg = 1810 # assume 1810 kcal per kg of dairy&eggs
        elif food_type == globals.FTVEGETABLE:
            exp_min = 5 # days 
            exp_max = 15 # days
            kg = 0.116*servings # assume 116g f,v per serving
            price = 3.62*2.2*kg # assume $3.62/lb to total for kg
            kcal_kg = 790 # assume 790 kcal per kg of f,v
            inedible_parts = 0.1
        elif food_type == globals.FTDRYFOOD:
            exp_min = 7 # days 
            exp_max = 8*7 # days
            kg = 0.065*servings # assume 65g per serving
            price = 1.5*2.2*kg # assume $1.50/lb to total for kg 
            kcal_kg = 3360 # assume 3360 kcal per kg
        elif food_type == globals.FTSNACKS:
            exp_min = 7 # days 
            exp_max = 8*7 # days
            kg = 0.095*servings # assume 95g per serving
            price = 3.3*2.2*kg # assume $3.30/lb to total for kg
            kcal_kg = 2790 # assume 2790 kcal per kg
        elif food_type == globals.FTSTOREPREPARED:
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
            'Inedible Parts': inedible_parts,
            'ServingsPerType': servings_per_type
            }
        assert new_food['ServingsPerType'].values.sum() >=  0
        assert not new_food['ServingsPerType'].isnull().values.any()
        return new_food