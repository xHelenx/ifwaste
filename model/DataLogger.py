import pandas as pd 
import globals

import datetime
import os
from pathlib import Path

class DataLogger: 

    def __init__(self) -> None:
        columns = [
            'Household',
            'Day',
            'Type',
            'Kg',
            'Price',
            'Servings',
            'Kcal',
            'Exp',
            globals.FGMEAT,
            globals.FGDAIRY,
            globals.FGVEGETABLE,
            globals.FGDRYFOOD,
            globals.FGSNACKS,
            globals.FGSTOREPREPARED
        ]
        
        self.log_bought = pd.DataFrame(columns=columns)
        self.log_eaten = pd.DataFrame(columns=columns)
        self.log_still_have = pd.DataFrame(columns=columns)
        
        self.log_wasted = pd.DataFrame(columns=[
            'Household',
            'Day Wasted',
            'Type',
            'Kg',
            'Price',
            'Servings',
            'Kcal',
            'Status',
            globals.FGMEAT,
            globals.FGDAIRY,
            globals.FGVEGETABLE,
            globals.FGDRYFOOD,
            globals.FGSNACKS,
            globals.FGSTOREPREPARED
        ])
        
        self.log_daily = pd.DataFrame(columns=[
            'Day',
            'Household',
            "Budget",
            "Servings",
            "Kcal", 
            "EEF", 
            "Cooked", 
            "AteLeftOvers",
            "QuickCook"
        ])
        self.log_configuration = pd.DataFrame(columns=[
            "Household",
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
        
        self.log_stores = pd.DataFrame(columns=[
            "Store",
            "Day",
            "Type",
            "Servings",
            "DaysTillExpiry",
            "PricePerServing",
            "SaleType",
            "Amount"
        ])
        
    
    def log_households_config(self,houses): 
        for house in houses: 
            self.log_configuration.loc[house.id] = {
                "Household" : house.id, 
                "RequiredKcal" : house.kcal,
                "RequiredServings" : house.req_servings,
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
            
    def log_households_daily(self,houses, day):
        """Collects the daily data from each house

        Args:
            house (Household): current household
            day (int): current day
        """     
        for house in houses: 
            for food in house.log_bought:
                self.log_bought.loc[len(self.log_bought)] = {
                    'Household': house.id,
                    'Day Bought': day,
                    'Type': food.type,
                    'Kg': food.kg,
                    'Price': food.price_kg*food.kg,
                    'Servings': food.servings,
                    'Kcal':food.kcal_kg*food.kg,
                    'Exp': food.exp,
                    globals.FGMEAT: food.servings_per_type[globals.FGMEAT].values[0],
                    globals.FGDAIRY: food.servings_per_type[globals.FGDAIRY].values[0],
                    globals.FGVEGETABLE: food.servings_per_type[globals.FGVEGETABLE].values[0],
                    globals.FGDRYFOOD: food.servings_per_type[globals.FGDRYFOOD].values[0],
                    globals.FGSNACKS: food.servings_per_type[globals.FGSNACKS].values[0],
                    globals.FGSTOREPREPARED: food.servings_per_type[globals.FGSTOREPREPARED].values[0]
                }
        house.log_bought = []
        for food in house.log_eaten:
            self.log_eaten.loc[len(self.log_eaten)] = {
                'Household': house.id,
                'Day Eaten': day,
                'Type': food.type,
                'Kg': food.kg,
                'Price':food.price_kg*food.kg,
                'Servings': food.servings,
                'Kcal': food.kcal_kg*food.kg,
                'Exp': food.exp,
                globals.FGMEAT: food.servings_per_type[globals.FGMEAT].values[0],
                globals.FGDAIRY: food.servings_per_type[globals.FGDAIRY].values[0],
                globals.FGVEGETABLE: food.servings_per_type[globals.FGVEGETABLE].values[0],
                globals.FGDRYFOOD: food.servings_per_type[globals.FGDRYFOOD].values[0],
                globals.FGSNACKS: food.servings_per_type[globals.FGSNACKS].values[0],
                globals.FGSTOREPREPARED: food.servings_per_type[globals.FGSTOREPREPARED].values[0]
            }
        house.log_eaten = []
        for food in house.log_wasted:
            self.log_wasted.loc[len(self.log_wasted)] = {
                'Household': house.id,
                'Day Wasted':day,
                'Type': food.type,
                'Kg': food.kg,
                'Price': food.price_kg*food.kg,
                'Servings': food.servings,
                'Kcal': food.kcal_kg*food.kg,
                'Exp': food.exp,
                'Status': food.status,
                globals.FGMEAT: food.servings_per_type[globals.FGMEAT].values[0],
                globals.FGDAIRY: food.servings_per_type[globals.FGDAIRY].values[0],
                globals.FGVEGETABLE: food.servings_per_type[globals.FGVEGETABLE].values[0],
                globals.FGDRYFOOD: food.servings_per_type[globals.FGDRYFOOD].values[0],
                globals.FGSNACKS: food.servings_per_type[globals.FGSNACKS].values[0],
                globals.FGSTOREPREPARED: food.servings_per_type[globals.FGSTOREPREPARED].values[0]
            }
        house.log_wasted = []
        self.log_daily.loc[len(self.log_daily)] = {
            'Household': house.id,
            'Day':day,
            'Budget':house.current_budget,
            "Servings":house.todays_servings,
            "Kcal":house.todays_kcal,            
            "EEF": house.log_today_eef, 
            "Cooked": house.log_today_cooked, 
            "AteLeftOvers": house.log_today_leftovers,
            "QuickCook":house.log_today_quickcook
        }
        
    
    def log_households_left_resources(self, houses,day): 
        """Tracks the final content of the storage, used after simulation is finished

        Args:
            house (House): house to track the storage off
        """        
        
        for house in houses: 
            for food in house.fridge.current_items:
                self.log_still_have.loc[len(self.log_still_have)] = {
                    'Day' : day ,
                    'Household': house.id,
                    'Type': food.type,
                    'Kg': food.kg,
                    'Price': food.price_kg*food.kg,
                    'Servings': food.servings,
                    'Kcal': food.kcal_kg*food.kg,
                    'Exp': food.exp,
                    'Status': food.status,
                    globals.FGMEAT: food.servings_per_type[globals.FGMEAT].values[0],
                    globals.FGDAIRY: food.servings_per_type[globals.FGDAIRY].values[0],
                    globals.FGVEGETABLE: food.servings_per_type[globals.FGVEGETABLE].values[0],
                    globals.FGDRYFOOD: food.servings_per_type[globals.FGDRYFOOD].values[0],
                    globals.FGSNACKS: food.servings_per_type[globals.FGSNACKS].values[0],
                    globals.FGSTOREPREPARED: food.servings_per_type[globals.FGSTOREPREPARED].values[0]
                }
            for food in house.pantry.current_items:
                self.log_still_have.loc[len(self.log_still_have)] = {
                    'Day' : day ,
                    'Household': house.id,
                    'Type': food.type,
                    'Kg': food.kg,
                    'Price': food.price_kg*food.kg,
                    'Servings': food.servings,
                    'Kcal': food.kcal_kg*food.kg,
                    'Exp': food.exp,
                    globals.FGMEAT: food.servings_per_type[globals.FGMEAT].values[0],
                    globals.FGDAIRY: food.servings_per_type[globals.FGDAIRY].values[0],
                    globals.FGVEGETABLE: food.servings_per_type[globals.FGVEGETABLE].values[0],
                    globals.FGDRYFOOD: food.servings_per_type[globals.FGDRYFOOD].values[0],
                    globals.FGSNACKS: food.servings_per_type[globals.FGSNACKS].values[0],
                    globals.FGSTOREPREPARED: food.servings_per_type[globals.FGSTOREPREPARED].values[0]
                }
                
    def log_stores_daily(self,stores, day):   
        for store in stores: 
            for _,row in store.stock.iterrows(): 
                self.log_stores.loc[len(self.log_stores)] = {
                    "Store": str(store),
                    "Day":day,
                    "Type": row["type"],
                    "Servings": row["servings"],
                    "DaysTillExpiry": row["days_till_expiry"],
                    "PricePerServing": row["price_per_serving"],
                    "SaleType": row["sale_type"],
                    "Amount": row["amount"]
                }
     
    def data_to_csv(self, experiment_name=None, run=None): 
        """Saves the finished tracked data to csv files
        """        
        path = str(Path(__file__).parents[1])
        dt = datetime.datetime.now()
        if (not os.path.isdir(path + "//"+ globals.SIMULATION_OUTPUTFOLDER )): 
            os.mkdir(path + "//"+ globals.SIMULATION_OUTPUTFOLDER + "//")
        
        if experiment_name != None: 
            path = path + "//"+ globals.SIMULATION_OUTPUTFOLDER + "//" + experiment_name + "//"
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
        self.log_daily.to_csv( path + foldername+ "/hh_daily.csv")
        self.log_configuration.to_csv( path + foldername+ "/config.csv")
        self.log_stores.to_csv( path + foldername+ "/stores_daily.csv")