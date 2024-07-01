

import pandas as pd
import globals
import json

from FoodGroups import FoodGroups



class Store():
    def __init__(self, store_type:str, location ) -> None:
        self.quality = 0.5 #todo
        self.price = 0.5 #todo calc based on stock avg p serving?
        self.food_groups = FoodGroups.get_instance()
        self.location = location
        with open(globals.CONFIG_PATH) as f: 
            config = json.load(f)
            self.product_range = pd.read_csv(config["Store"][store_type]["product_range"])

        self.stock = pd.DataFrame(columns= [
            'type', 
            'servings', 
            'exp_min', 
            'exp_max',
            'price_per_serving',
            'kg_per_serving',
            'kcal_per_kg',
            'inedible_percentage',
            'amount'])        
        
        self.buy_stock(10)
        

        
    
    def buy_stock(self, amount_per_item): 
        
        for (i,_) in self.product_range.iterrows(): 
            curr_fg = self.food_groups.get_food_group(self.product_range.loc[i,"type"])           
            mask = (self.stock["type"] == self.product_range.loc[i,"type"]) & (self.stock["servings"] == self.product_range.loc[i,"servings"] ) & (self.stock["price_per_serving"] == self.product_range.loc[i,"price_per_serving"])
            if len(self.stock[mask]) > 0:
                self.stock.loc[mask,"amount"] += amount_per_item
            else: 
                new_item = [self.product_range.loc[i,"type"],
                            self.product_range.loc[i,"servings"],
                            curr_fg["exp_min"], 
                            curr_fg["exp_min"],
                            self.product_range.loc[i,"price_per_serving"], 
                            curr_fg["kg_per_serving"], 
                            curr_fg["kcal_per_kg"], 
                            curr_fg["inedible_percentage"], 
                            amount_per_item]
                        
                self.stock.loc[len(self.stock)] = new_item                            
             
    def get_available_fg(self): 
        return self.stock["type"].unique()