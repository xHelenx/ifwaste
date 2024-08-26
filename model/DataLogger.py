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
        """
        initalizes DataLogger.
        
        Class variables:
        
        self.logs (dict): dictionary logname:str -> data:pd.Dataframe
        self.foldername (str): folder to write results to
        
        """         
        self.logs = dict()
        self.reset_logs()   
        self.foldername:str = ""
        
        self.logs["log_hh_config"] = pd.DataFrame(columns=[
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
        
        self.logs["log_sim_config"] = pd.DataFrame(columns=
                                                   ["total_days"])
        
    
    def log_configs(self,houses:list[Household]) -> None:  # type: ignore
        """Log the household configuration and simulation configurations.

        Args:
            houses (list[Household]): houses to log the information for
        """        
        
        
        
        self.logs["log_sim_config"].loc[0, "total_days"] = globals.SIMULATION_DAYS

        for house in houses: 
            self.logs["log_hh_config"].loc[house.id] = { # type: ignore
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
            houses (list[Household]): houses to log the information for
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
            houses (list[Household]): houses to log the information for
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
        """Collects the daily data from each store

        Args:
            stores (list[Stores]): stores to log the information for
        """
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
    
    def data_to_csv(self, run:int, logs_to_write: list[str]|None=None) -> None: 
        """Saves the finished tracked data to csv files

        Args:
            run (int): Number of simulation run, used to write folder_name
            logs_to_write (list[str] | None, optional): logs_to_write, None defaults to all logs in self.logs. Defaults to None.
        """                
        path = self._create_folder(run)
        
        
        if not logs_to_write is None: 
            for item in logs_to_write: 
                config_header = True
                config_path = path + self.foldername + f"//"+ item + ".csv"
                if os.path.exists(config_path):
                   config_header = False
                self.logs[item].to_csv(config_path, header=config_header, mode="a")
        else:
            for log_name, log_file in self.logs.items():
                if not log_name == "log_hh_config" and not log_name == "log_sim_config":
                    file_path = path + self.foldername + "//" + log_name + ".csv"
                    log_header = True
                    if os.path.exists(file_path):
                        log_header = False
                    log_file.to_csv(file_path, header=log_header, mode="a")
                    self.reset_logs()
       
    
    def _create_folder(self, run:int)  -> str:
        """creates the folder name and returns it. Will be used for 
        all log files of that run. 

        Args:
            run (int): simulation run id, for folder creation

        Returns:
            str: foldername
        """        
        path = str(Path(__file__).parents[1])
        dt = datetime.datetime.now()
        if (not os.path.isdir(path + "//"+ globals.SIMULATION_OUTPUTFOLDER )): 
            os.mkdir(path + "//"+ globals.SIMULATION_OUTPUTFOLDER + "//")
        
        if globals.EXPERIMENT_NAME != None: 
            path = path + "//"+ globals.SIMULATION_OUTPUTFOLDER + "//" + globals.EXPERIMENT_NAME + "//"
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
        """Empties the daily logs for the next day.
        """        
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
        """Adds new data to the log in self.log, defined by log_key

        Args:
            id (int): household id 
            log_key (str): string specifying which log to append the data to ["log_wasted", "log_eaten",
            "log_bought"]
            data (pd.DataFrame | pd.Series | None): data to be added

        Raises:
            ValueError: _description_
        """        
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
        """adds data to the waste log

        Args:
            data (pd.DataFrame): data to be added
        """        
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
        """adds data to the eaten log

        Args:
            data (pd.DataFrame): data to be added
        """  
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
        """adds data to the bought log

        Args:
            data (pd.DataFrame): data to be added
        """  
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