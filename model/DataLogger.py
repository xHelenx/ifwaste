from __future__ import annotations
from multiprocessing import Value

import pandas as pd 
import globals

import datetime
import os
from pathlib import Path

from FoodGroups import FoodGroups
from Store import Store



class DataLogger: 

    def __init__(self) -> None:             
        self.logs = dict()
        self.reset_logs()   
        self.foldername:str = ""
        
        self.logs["log_config"] = pd.DataFrame(columns=[
            "household",
            "required_servings",
            "budget",
            "adults",
            "children",
            "lvl_of_concern",
            "plate_waste_ratio",
            "avail_time_monday",
            "avail_time_tuesday",
            "avail_time_wednesday",
            "avail_time_thursday",
            "avail_time_friday",
            "avail_time_saturday",
            "avail_time_sunday",
            "shopping_frequency",
            "total_runs"            
        ])
        
    
    def log_households_config(self,houses:list[Household]) -> None:  # type: ignore
        for house in houses: 
            self.logs["log_config"].loc[house.id] = { # type: ignore
                "household" :  house.id, 
                "required_servings" :  house.req_servings,
                "budget" :  house.budget, 
                "adults" :  house.amount_adults,
                "children" : house.amount_children,    
                "lvl_of_concern" : house.household_concern,
                "plate_waste_ratio" : house.cookingManager.household_plate_waste_ratio, 
                "avail_time_monday" :  house.cookingManager.time[0], 
                "avail_time_tuesday" :  house.cookingManager.time[1], 
                "avail_time_wednesday" :  house.cookingManager.time[2], 
                "avail_time_thursday" :  house.cookingManager.time[3], 
                "avail_time_friday" :  house.cookingManager.time[4], 
                "avail_time_saturday" :  house.cookingManager.time[5], 
                "avail_time_sunday" :  house.cookingManager.time[6],
                "shopping_frequency" : house.shopping_frequency,
                "total_runs" :  globals.SIMULATION_RUNS
    }
            
    def log_households_daily(self,houses:list[Household]) -> None: # type: ignore
        """Collects the daily data from each house

        Args:
            house (household): current household
        """     
        for house in houses: 
            self.logs["log_hh_daily"].loc[len(self.logs["log_hh_daily"])] = { # type: ignore
                "household": house.id,
                "day":globals.DAY,
                "budget":house.shoppingManager.todays_budget,
                "servings":house.cookingManager.todays_servings,      
                "EEF": house.log_today_eef, 
                "cooked": house.log_today_cooked, 
                "ate_leftovers": house.log_today_leftovers,
                "quick_cook":house.log_today_quickcook,
                "shopping_time": house.shoppingManager.log_shopping_time
            }
    
    def log_households_left_resources(self, houses:list[Household]) -> None:  # type: ignore
        """Tracks the final content of the storage, used after simulation is finished

        Args:
            house (House): house to track the storage off
        """   
        for house in houses: 
            for storage in [house.fridge, house.pantry]:
                for i in storage.current_items.index:
                    item = storage.current_items.loc[i]
                    self.logs["log_still_have"].loc[len(self.logs["log_still_have"])] = { # type: ignore
                        "household": house.id,
                        "price": item["price"],
                        "servings": item["servings"],
                        "days_till_expiry": item["days_till_expiry"],
                        "status": item["status"],
                        globals.FGMEAT: item[globals.FGMEAT],
                        globals.FGDAIRY: item[globals.FGDAIRY],
                        globals.FGVEGETABLE: item[globals.FGVEGETABLE],
                        globals.FGDRYFOOD: item[globals.FGDRYFOOD],
                        globals.FGSNACKS: item[globals.FGSNACKS],
                        globals.FGSTOREPREPARED: item[globals.FGSTOREPREPARED]
                    } 
    
    def log_stores_daily(self,stores:list[Store]) -> None:   
        for store in stores: 
            for index in store.stock.index: 
                item = store.stock.loc[index]
                self.logs["log_store_daily"].loc[len(self.logs["log_store_daily"])] = { # type: ignore
                    "day":globals.DAY,
                    "store": str(store),
                    "type": item["type"],
                    "servings": item["servings"],
                    "days_till_expiry": item["days_till_expiry"],
                    "price_per_serving": item["price_per_serving"],
                    "sale_type": item["sale_type"],
                    "amount": item["amount"]
                }
    
    def data_to_csv(self, experiment_name:str|None=None, run:int|None=None, logs_to_write: list[str]|None=None) -> None: 
        """Saves the finished tracked data to csv files
        """        
        path = self._create_folder(experiment_name, run)
        
        
        if not logs_to_write is None: 
            for item in logs_to_write: 
                config_header = True
                config_path = path + self.foldername + f"//"+ item + ".csv"
                if os.path.exists(config_path):
                   config_header = False
                self.logs[item].to_csv(config_path, header=config_header, mode="a")
        else:
            for log_name, log_file in self.logs.items():
                if not log_name == "log_config":
                    file_path = path + self.foldername + "//" + log_name + ".csv"
                    log_header = True
                    if os.path.exists(file_path):
                        log_header = False
                    log_file.to_csv(file_path, header=log_header, mode="a")
                    self.reset_logs()
       
    
    def _create_folder(self,experiment_name:str|None, run:int | None)  -> str:
        path = str(Path(__file__).parents[1])
        dt = datetime.datetime.now()
        if (not os.path.isdir(path + "//"+ globals.SIMULATION_OUTPUTFOLDER )): 
            os.mkdir(path + "//"+ globals.SIMULATION_OUTPUTFOLDER + "//")
        
        if experiment_name != None: 
            path = path + "//"+ globals.SIMULATION_OUTPUTFOLDER + "//" + experiment_name + "//"
            if (not os.path.isdir(path )): 
                os.mkdir(path)
        
        if self.foldername == "":
            if run != None: #either save by run id 
                self.foldername = "run_" + str(run)
                if (os.path.isdir(path + self.foldername)): #just in case
                    self.foldername += f"_{dt.date().__str__()}at{dt.time().__str__()[:2]}-{dt.time().__str__()[3:5]}"
            else:  #or by date if it is a single experiment
                self.foldername = f"{dt.date().__str__()}at{dt.time().__str__()[:2]}-{dt.time().__str__()[3:5]}"
        
        if not (os.path.isdir(path + self.foldername)): 
            os.mkdir(path + self.foldername)
                
        return path
                    
    def reset_logs(self) -> None: 
        self.logs = {    
        "log_bought" : pd.DataFrame(
            columns=["household","day","type","servings","sale_type",
                    "days_till_expiry","price_per_serving"]),
        "log_eaten" : pd.DataFrame(
            columns=["household","day","price","servings","days_till_expiry","status",
                     globals.FGMEAT,globals.FGDAIRY,globals.FGVEGETABLE,globals.FGDRYFOOD,globals.FGSNACKS,
                     globals.FGSTOREPREPARED]),
        "log_still_have" : pd.DataFrame(
            columns=["household","price","servings","days_till_expiry","status",
                     globals.FGMEAT,globals.FGDAIRY,globals.FGVEGETABLE,globals.FGDRYFOOD,globals.FGSNACKS,
                     globals.FGSTOREPREPARED]),
        "log_wasted" : pd.DataFrame(
            columns=["household","day","price","servings","days_till_expiry","status","reason",
                     globals.FGMEAT,globals.FGDAIRY,globals.FGVEGETABLE,globals.FGDRYFOOD,globals.FGSNACKS,
                     globals.FGSTOREPREPARED]),
        "log_store_daily" : pd.DataFrame(
            columns=["day","store","type","servings","days_till_expiry",
                     "price_per_serving","sale_type","amount"]),
        "log_hh_daily" : pd.DataFrame(
            columns=["household","day","budget","servings","EEF","cooked","ate_leftovers","quick_cook","shopping_time"])
        }
               
        
    def append_log(self, id:int, log_key:str, data:pd.DataFrame | pd.Series  | None ) -> None:
        if not data is None: 
            data_copy = data.copy()
            if isinstance(data_copy, pd.DataFrame):
                data_copy["household"] = id
                data_copy["day"] = globals.DAY
                
            else:
                data_copy = data_copy.to_frame().T
                data_copy["household"] = id
                data_copy["day"] = globals.DAY
            data_copy = pd.DataFrame(data_copy)
           
        
            if log_key == "log_wasted": 
                self._log_waste(data=data_copy)
            elif log_key == "log_eaten": 
                self._log_eaten(data=data_copy)
            elif log_key == "log_bought": 
                self._log_bought(data=data_copy)
            else: 
                raise ValueError("logger does not exist")
                
    
    def _log_waste(self,data:pd.DataFrame) -> None: 
        for _, item in data.iterrows():
            self.logs["log_wasted"].loc[len(self.logs["log_wasted"])] = { # type: ignore
            "household": item["household"],
            "day": globals.DAY,
            "servings": item["servings"],
            "days_till_expiry": item["days_till_expiry"],
            "status": item["status"],
            "price": item["price"],
            "reason":item["reason"],
            globals.FGMEAT: item[globals.FGMEAT],
            globals.FGDAIRY: item[globals.FGDAIRY],
            globals.FGVEGETABLE: item[globals.FGVEGETABLE],
            globals.FGDRYFOOD: item[globals.FGDRYFOOD],
            globals.FGSNACKS: item[globals.FGSNACKS],
            globals.FGSTOREPREPARED: item[globals.FGSTOREPREPARED]
        }
    def _log_eaten(self,data:pd.DataFrame) -> None:
            for _, item in data.iterrows():
                self.logs["log_eaten"].loc[len(self.logs["log_eaten"])] = { # type: ignore
                "household": item["household"],
                "day": globals.DAY,
                "price": item["price"],
                "servings": item["servings"],
                "days_till_expiry": item.days_till_expiry,
                "status": item["status"],
                globals.FGMEAT: item[globals.FGMEAT],
                globals.FGDAIRY: item[globals.FGDAIRY],
                globals.FGVEGETABLE: item[globals.FGVEGETABLE],
                globals.FGDRYFOOD: item[globals.FGDRYFOOD],
                globals.FGSNACKS: item[globals.FGSNACKS],
                globals.FGSTOREPREPARED: item[globals.FGSTOREPREPARED]
                
            }
                
    def _log_bought(self,data:pd.DataFrame) -> None:
        for _, item in data.iterrows():
            self.logs["log_bought"].loc[len(self.logs["log_bought"])] = { # type: ignore
                "household": item["household"],
                "day": globals.DAY,
                "type": item["type"],
                "servings": item["servings"],
                "days_till_expiry": item["days_till_expiry"],
                "price_per_serving":item["price_per_serving"],
                "sale_type":item["sale_type"]
            }