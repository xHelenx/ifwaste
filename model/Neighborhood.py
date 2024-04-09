
import datetime
import os
from pathlib import Path
from House import House
from Store import Store
import pandas as pd

from globalValues import *


class Neighborhood():
    def __init__(self, houses:list):
        self.houses = houses
        store = Store()
        for house in self.houses: 
            house.add_store(store)
            
        self.log_bought = pd.DataFrame(columns=[
            'House',
            'Day Bought',
            'Type',
            'kg',
            'Price',
            'Servings',
            'kcal',
            'Exp',
            FTMEAT,
            FTDAIRY,
            FTVEGETABLE,
            FTDRYFOOD,
            FTSNACKS,
            FTSTOREPREPARED
        ])
        self.log_eaten = pd.DataFrame(columns=[
            'House',
            'Day Eaten',
            'Type',
            'kg',
            'Price',
            'Servings',
            'kcal',
            'Exp',
            FTMEAT,
            FTDAIRY,
            FTVEGETABLE,
            FTDRYFOOD,
            FTSNACKS,
            FTSTOREPREPARED
        ])
        self.log_wasted = pd.DataFrame(columns=[
            'House',
            'Day Wasted',
            'Type',
            'kg',
            'Price',
            'Servings',
            'kcal',
            'Status',
            FTMEAT,
            FTDAIRY,
            FTVEGETABLE,
            FTDRYFOOD,
            FTSNACKS,
            FTSTOREPREPARED
        ])
        self.log_still_have = pd.DataFrame(columns=[
            'House',
            'Type',
            'kg',
            'Price',
            'Servings',
            'kcal',
            'Exp',
            FTMEAT,
            FTDAIRY,
            FTVEGETABLE,
            FTDRYFOOD,
            FTSNACKS,
            FTSTOREPREPARED
        ])
        self.log_daily = pd.DataFrame(columns=[
            'Day',
            'House',
            "Budget",
            "Servings",
            "Kcal"
        ])
        self.log_configuration = pd.DataFrame(columns=[
            "House",
            "RequiredKcal",
            "ReqServings",
            "Budget",
            "IsServingBased"
        ])
        
        for house in self.houses: 
            self.log_configuration.loc[house.id] = {
               "House" : house.id, 
                "RequiredKcal" : house.kcal,
                "ReqServings" : house.servings,
                "Budget" : house.budget, 
                "IsServingBased" : house.is_serving_based
            }
        
    def run(self, days= 365):
        for i in range(days):
            for house in self.houses:
                house.do_a_day(day=i)
                self.collect_data(house=house, day=i)
        for house in self.houses:
            self.get_storage(house=house)
    def collect_data(self, house: House, day: int):
        for food in house.log_bought:
            self.log_bought.loc[len(self.log_bought)] = {
                'House': house.id,
                'Day Bought': day,
                'Type': food.type,
                'kg': food.kg,
                'Price': food.price_kg*food.kg,
                'Servings': food.servings,
                'kcal':food.kcal_kg*food.kg,
                'Exp': food.exp,
                FTMEAT: food.servings_per_type[FTMEAT].values[0],
                FTDAIRY: food.servings_per_type[FTDAIRY].values[0],
                FTVEGETABLE: food.servings_per_type[FTVEGETABLE].values[0],
                FTDRYFOOD: food.servings_per_type[FTDRYFOOD].values[0],
                FTSNACKS: food.servings_per_type[FTSNACKS].values[0],
                FTSTOREPREPARED: food.servings_per_type[FTSTOREPREPARED].values[0]
            }
            house.log_bought.remove(food)
        for food in house.log_eaten:
            self.log_eaten.loc[len(self.log_eaten)] = {
                'House': house.id,
                'Day Eaten': day,
                'Type': food.type,
                'kg': food.kg,
                'Price':food.price_kg*food.kg,
                'Servings': food.servings,
                'kcal': food.kcal_kg*food.kg,
                'Exp': food.exp,
                FTMEAT: food.servings_per_type[FTMEAT].values[0],
                FTDAIRY: food.servings_per_type[FTDAIRY].values[0],
                FTVEGETABLE: food.servings_per_type[FTVEGETABLE].values[0],
                FTDRYFOOD: food.servings_per_type[FTDRYFOOD].values[0],
                FTSNACKS: food.servings_per_type[FTSNACKS].values[0],
                FTSTOREPREPARED: food.servings_per_type[FTSTOREPREPARED].values[0]
            }
            house.log_eaten.remove(food)
        for food in house.log_wasted:
            self.log_wasted.loc[len(self.log_wasted)] = {
                'House': house.id,
                'Day Wasted':day,
                'Type': food.type,
                'kg': food.kg,
                'Price': food.price_kg*food.kg,
                'Servings': food.servings,
                'kcal': food.kcal_kg*food.kg,
                'Exp': food.exp,
                'Status': food.status,
                FTMEAT: food.servings_per_type[FTMEAT].values[0],
                FTDAIRY: food.servings_per_type[FTDAIRY].values[0],
                FTVEGETABLE: food.servings_per_type[FTVEGETABLE].values[0],
                FTDRYFOOD: food.servings_per_type[FTDRYFOOD].values[0],
                FTSNACKS: food.servings_per_type[FTSNACKS].values[0],
                FTSTOREPREPARED: food.servings_per_type[FTSTOREPREPARED].values[0]
            }
            house.log_wasted.remove(food)
        self.log_daily.loc[len(self.log_daily)] = {
            'House': house.id,
            'Day':day,
            'Budget':house.current_budget,
            "Servings":house.todays_servings,
            "Kcal":house.todays_kcal,
        }
    def get_storage(self, house: House):
        for food in house.fridge.current_items:
            self.log_still_have.loc[len(self.log_still_have)] = {
                'House': house.id,
                'Type': food.type,
                'kg': food.kg,
                'Price': food.price_kg*food.kg,
                'Servings': food.servings,
                'kcal': food.kcal_kg*food.kg,
                'Exp': food.exp,
                'Status': food.status,
                FTMEAT: food.servings_per_type[FTMEAT].values[0],
                FTDAIRY: food.servings_per_type[FTDAIRY].values[0],
                FTVEGETABLE: food.servings_per_type[FTVEGETABLE].values[0],
                FTDRYFOOD: food.servings_per_type[FTDRYFOOD].values[0],
                FTSNACKS: food.servings_per_type[FTSNACKS].values[0],
                FTSTOREPREPARED: food.servings_per_type[FTSTOREPREPARED].values[0]
            }
            house.fridge.remove(food)
        for food in house.pantry.current_items:
            self.log_still_have.loc[len(self.log_still_have)] = {
                'House': house.id,
                'Type': food.type,
                'kg': food.kg,
                'Price': food.price_kg*food.kg,
                'Servings': food.servings,
                'kcal': food.kcal_kg*food.kg,
                'Exp': food.exp,
                FTMEAT: food.servings_per_type[FTMEAT].values[0],
                FTDAIRY: food.servings_per_type[FTDAIRY].values[0],
                FTVEGETABLE: food.servings_per_type[FTVEGETABLE].values[0],
                FTDRYFOOD: food.servings_per_type[FTDRYFOOD].values[0],
                FTSNACKS: food.servings_per_type[FTSNACKS].values[0],
                FTSTOREPREPARED: food.servings_per_type[FTSTOREPREPARED].values[0]
            }
            house.pantry.remove(food)
    def data_to_csv(self):
        path = str(Path(__file__).parents[1])
        dt = datetime.datetime.now()
        foldername = f'{dt.date().__str__()}at{dt.time().__str__()[:2]}-{dt.time().__str__()[3:5]}'
        if (not os.path.isdir(path + "\\data")): 
            os.mkdir(path + "\\data\\")
        
        os.mkdir(path + "\\data\\" + foldername)
            
        
        self.log_bought.to_csv( path + "\\data\\" + foldername+ "/bought.csv")
        self.log_eaten.to_csv( path + "\\data\\" + foldername+ "/eaten.csv")
        self.log_wasted.to_csv( path + "\\data\\" + foldername+ "/wasted.csv")
        self.log_still_have.to_csv( path + "\\data\\" + foldername+ "/still_have.csv")
        self.log_daily.to_csv( path + "\\data\\" + foldername+ "/daily.csv")
        self.log_configuration.to_csv( path + "\\data\\" + foldername+ "/config.csv")
        