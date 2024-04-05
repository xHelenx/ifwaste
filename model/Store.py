import numpy as np
import pandas as pd
from globalValues import * 

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
        self.stock_shelves()
        #self.inventory = []
    
    def stock_shelves(self):
        """Stocks shelves with different food types and serving sizes
        """    
        food_types = [
            FTMEAT,
            FTDAIRY,
            FTVEGETABLE,
            FTDRYFOOD,
            FTSNACKS,
            FTSTOREPREPARED
            ]
        for food_type in food_types:
            self.shelves = self.shelves._append(self.food_data(food_type=food_type, servings=6), ignore_index=True)
            self.shelves = self.shelves._append(self.food_data(food_type=food_type, servings=12), ignore_index=True)
            self.shelves = self.shelves._append(self.food_data(food_type=food_type, servings=20), ignore_index=True)

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
        
        zero_array = np.zeros(shape=(1,TOTAL_FOOD_TYPES))
        servings_per_type = pd.DataFrame(zero_array, columns= [
            FTMEAT,
            FTDAIRY,
            FTVEGETABLE,
            FTDRYFOOD,
            FTSNACKS,
            FTSTOREPREPARED
            ])
        servings_per_type[food_type] = servings 
        assert servings_per_type.values.sum() > 0
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
            'Inedible Parts': inedible_parts,
            'ServingsPerType': servings_per_type
            }
        assert new_food['ServingsPerType'].values.sum() >=  0
        assert not new_food['ServingsPerType'].isnull().values.any()
        return new_food