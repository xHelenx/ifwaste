
import datetime
import os
from pathlib import Path
from House import House
from Store import Store
import pandas as pd
import globals 


class Neighborhood():
    def __init__(self, houses:list):
        """Initializes the neighborhood, by assigning the store to the houses 
        and setting up logging 

        Args:
            houses (list): _description_
        """        
        self.houses = houses
        store = Store()
        for house in self.houses: 
            house.add_store(store)
            
        self.log_bought = pd.DataFrame(columns=[
            'House',
            'Day Bought',
            'Type',
            'Kg',
            'Price',
            'Servings',
            'Kcal',
            'Exp',
            globals.FTMEAT,
            globals.FTDAIRY,
            globals.FTVEGETABLE,
            globals.FTDRYFOOD,
            globals.FTSNACKS,
            globals.FTSTOREPREPARED
        ])
        self.log_eaten = pd.DataFrame(columns=[
            'House',
            'Day Eaten',
            'Type',
            'Kg',
            'Price',
            'Servings',
            'Kcal',
            'Exp',
            globals.FTMEAT,
            globals.FTDAIRY,
            globals.FTVEGETABLE,
            globals.FTDRYFOOD,
            globals.FTSNACKS,
            globals.FTSTOREPREPARED
        ])
        self.log_wasted = pd.DataFrame(columns=[
            'House',
            'Day Wasted',
            'Type',
            'Kg',
            'Price',
            'Servings',
            'Kcal',
            'Status',
            globals.FTMEAT,
            globals.FTDAIRY,
            globals.FTVEGETABLE,
            globals.FTDRYFOOD,
            globals.FTSNACKS,
            globals.FTSTOREPREPARED
        ])
        self.log_still_have = pd.DataFrame(columns=[
            'Day',
            'House',
            'Type',
            'Kg',
            'Price',
            'Servings',
            'Kcal',
            'Exp',
            globals.FTMEAT,
            globals.FTDAIRY,
            globals.FTVEGETABLE,
            globals.FTDRYFOOD,
            globals.FTSNACKS,
            globals.FTSTOREPREPARED
        ])
        self.log_daily = pd.DataFrame(columns=[
            'Day',
            'House',
            "Budget",
            "Servings",
            "Kcal", 
            "EEF", 
            "Cooked", 
            "AteLeftOvers",
            "QuickCook",
            "QuickShop",
            "Enough_time",
            "Enough_ing"
        ])
        self.log_configuration = pd.DataFrame(columns=[
            "House",
            "RequiredKcal",
            "RequiredServings",
            "Budget",
            "IsServingBased",
            "Adults",
            "Children",
            'LvlOfConcern',
            'AvailTimeMonday',
            'AvailTimeTuesday',
            'AvailTimeWednesday',
            'AvailTimeThursday',
            'AvailTimeFriday',
            'AvailTimeSaturday',
            'AvailTimeSunday',
            'ShoppingFrequency',
            'totalRuns'            
        ])
        
        for house in self.houses: 
            self.log_configuration.loc[house.id] = {
                "House" : house.id, 
                "RequiredKcal" : house.kcal,
                "RequiredServings" : house.servings,
                "Budget" : house.budget, 
                "IsServingBased" : house.is_serving_based,
                "Adults" : house.amount_adults,
                "Children": house.amount_children,    
                "LvlOfConcern": house.household_concern,
                "PlateWasteRatio": house.household_plate_waste_ratio, 
                'AvailTimeMonday' : house.time[0], 
                'AvailTimeTuesday' : house.time[1], 
                'AvailTimeWednesday' : house.time[2], 
                'AvailTimeThursday' : house.time[3], 
                'AvailTimeFriday' : house.time[4], 
                'AvailTimeSaturday' : house.time[5], 
                'AvailTimeSunday' : house.time[6],
                'ShoppingFrequency': house.shopping_frequency,
                'totalRuns' : globals.SIMULATION_RUNS,
            }
        
    def run(self, days= 365):
        """Runs the simulation for the amount of days specified

        Args:
            days (int, optional): number of days to simulate. Defaults to 365.
        """        
        for i in range(days):
            print(i)
            for house in self.houses:
                house.do_a_day(day=i)
                self.collect_data(house=house, day=i)
                self.get_storage(house=house, day=i)
                
    def collect_data(self, house: House, day: int):
        """Collects the daily data from each house

        Args:
            house (House): current household
            day (int): current day
        """        
        for food in house.log_bought:
            self.log_bought.loc[len(self.log_bought)] = {
                'House': house.id,
                'Day Bought': day,
                'Type': food.type,
                'Kg': food.kg,
                'Price': food.price_kg*food.kg,
                'Servings': food.servings,
                'Kcal':food.kcal_kg*food.kg,
                'Exp': food.exp,
                globals.FTMEAT: food.servings_per_type[globals.FTMEAT].values[0],
                globals.FTDAIRY: food.servings_per_type[globals.FTDAIRY].values[0],
                globals.FTVEGETABLE: food.servings_per_type[globals.FTVEGETABLE].values[0],
                globals.FTDRYFOOD: food.servings_per_type[globals.FTDRYFOOD].values[0],
                globals.FTSNACKS: food.servings_per_type[globals.FTSNACKS].values[0],
                globals.FTSTOREPREPARED: food.servings_per_type[globals.FTSTOREPREPARED].values[0]
            }
        house.log_bought = []
        for food in house.log_eaten:
            self.log_eaten.loc[len(self.log_eaten)] = {
                'House': house.id,
                'Day Eaten': day,
                'Type': food.type,
                'Kg': food.kg,
                'Price':food.price_kg*food.kg,
                'Servings': food.servings,
                'Kcal': food.kcal_kg*food.kg,
                'Exp': food.exp,
                globals.FTMEAT: food.servings_per_type[globals.FTMEAT].values[0],
                globals.FTDAIRY: food.servings_per_type[globals.FTDAIRY].values[0],
                globals.FTVEGETABLE: food.servings_per_type[globals.FTVEGETABLE].values[0],
                globals.FTDRYFOOD: food.servings_per_type[globals.FTDRYFOOD].values[0],
                globals.FTSNACKS: food.servings_per_type[globals.FTSNACKS].values[0],
                globals.FTSTOREPREPARED: food.servings_per_type[globals.FTSTOREPREPARED].values[0]
            }
        house.log_eaten = []
        for food in house.log_wasted:
            self.log_wasted.loc[len(self.log_wasted)] = {
                'House': house.id,
                'Day Wasted':day,
                'Type': food.type,
                'Kg': food.kg,
                'Price': food.price_kg*food.kg,
                'Servings': food.servings,
                'Kcal': food.kcal_kg*food.kg,
                'Exp': food.exp,
                'Status': food.status,
                globals.FTMEAT: food.servings_per_type[globals.FTMEAT].values[0],
                globals.FTDAIRY: food.servings_per_type[globals.FTDAIRY].values[0],
                globals.FTVEGETABLE: food.servings_per_type[globals.FTVEGETABLE].values[0],
                globals.FTDRYFOOD: food.servings_per_type[globals.FTDRYFOOD].values[0],
                globals.FTSNACKS: food.servings_per_type[globals.FTSNACKS].values[0],
                globals.FTSTOREPREPARED: food.servings_per_type[globals.FTSTOREPREPARED].values[0]
            }
        house.log_wasted = []
        self.log_daily.loc[len(self.log_daily)] = {
            'House': house.id,
            'Day':day,
            'Budget':house.current_budget,
            "Servings":house.todays_servings,
            "Kcal":house.todays_kcal,            
            "EEF": house.log_today_eef, 
            "Cooked": house.log_today_cooked, 
            "AteLeftOvers": house.log_today_leftovers,
            "QuickCook":house.log_today_quickcook,
            "QuickShop":house.log_today_quickshop,
            "Enough_time": house.log_today_enough_time,
            "Enough_ing": house.log_today_enough_ing
        }
    def get_storage(self, house: House, day):
        """Tracks the final content of the storage, used aglobals.fter simulation is finished

        Args:
            house (House): house to track the storage off
        """        
        for food in house.fridge.current_items:
            self.log_still_have.loc[len(self.log_still_have)] = {
                'Day' : day ,
                'House': house.id,
                'Type': food.type,
                'Kg': food.kg,
                'Price': food.price_kg*food.kg,
                'Servings': food.servings,
                'Kcal': food.kcal_kg*food.kg,
                'Exp': food.exp,
                'Status': food.status,
                globals.FTMEAT: food.servings_per_type[globals.FTMEAT].values[0],
                globals.FTDAIRY: food.servings_per_type[globals.FTDAIRY].values[0],
                globals.FTVEGETABLE: food.servings_per_type[globals.FTVEGETABLE].values[0],
                globals.FTDRYFOOD: food.servings_per_type[globals.FTDRYFOOD].values[0],
                globals.FTSNACKS: food.servings_per_type[globals.FTSNACKS].values[0],
                globals.FTSTOREPREPARED: food.servings_per_type[globals.FTSTOREPREPARED].values[0]
            }
        for food in house.pantry.current_items:
            self.log_still_have.loc[len(self.log_still_have)] = {
                'Day' : day ,
                'House': house.id,
                'Type': food.type,
                'Kg': food.kg,
                'Price': food.price_kg*food.kg,
                'Servings': food.servings,
                'Kcal': food.kcal_kg*food.kg,
                'Exp': food.exp,
                globals.FTMEAT: food.servings_per_type[globals.FTMEAT].values[0],
                globals.FTDAIRY: food.servings_per_type[globals.FTDAIRY].values[0],
                globals.FTVEGETABLE: food.servings_per_type[globals.FTVEGETABLE].values[0],
                globals.FTDRYFOOD: food.servings_per_type[globals.FTDRYFOOD].values[0],
                globals.FTSNACKS: food.servings_per_type[globals.FTSNACKS].values[0],
                globals.FTSTOREPREPARED: food.servings_per_type[globals.FTSTOREPREPARED].values[0]
            }
    def data_to_csv(self, experiment_name=None, run=None): 
        """Saves the finished tracked data to csv files
        """        
        path = str(Path(__file__).parents[1])
        dt = datetime.datetime.now()
        if (not os.path.isdir(path + "//data")): 
            os.mkdir(path + "//data//")
        
        if experiment_name != None: 
            path = path + "//data//" + experiment_name + "//"
            if (not os.path.isdir(path )): 
                os.mkdir(path)
        
        foldername = ""              
        if run != None: #either save by run id 
            foldername = "run_" + str(run)
        else:  #or by date if it is a single experiment
            foldername = f'{dt.date().__str__()}at{dt.time().__str__()[:2]}-{dt.time().__str__()[3:5]}'
        os.mkdir(path + foldername)
        
        self.log_bought.to_csv( path + foldername+ "/bought.csv")
        self.log_eaten.to_csv( path + foldername+ "/eaten.csv")
        self.log_wasted.to_csv( path + foldername+ "/wasted.csv")
        self.log_still_have.to_csv( path + foldername+ "/still_have.csv")
        self.log_daily.to_csv( path + foldername+ "/daily.csv")
        self.log_configuration.to_csv( path + foldername+ "/config.csv")
        