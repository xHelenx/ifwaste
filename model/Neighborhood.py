
import datetime
import os
from pathlib import Path
from House import House
from Store import Store
import pandas as pd


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
        path = str(Path(__file__).parents[1])
        dt = datetime.datetime.now()
        foldername = f'{dt.date().__str__()}at{dt.time().__str__()[:2]}-{dt.time().__str__()[3:5]}'
        if (not os.path.isdir(path + "\\data")): 
            os.mkdir(path + "\\data\\")
        
        os.mkdir(path + "\\data\\" + foldername)
            
        
        self.bought.to_csv( path + "\\data\\" + foldername+ "/bought.csv")
        self.eaten.to_csv( path + "\\data\\" + foldername+ "/eaten.csv")
        self.wasted.to_csv( path + "\\data\\" + foldername+ "/wasted.csv")
        self.still_have.to_csv( path + "\\data\\" + foldername+ "/still_have.csv")