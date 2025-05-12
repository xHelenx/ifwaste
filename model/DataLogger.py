import datetime
import os
from pathlib import Path
import globals_config as globals_config
import pandas as pd
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
        ])
        
        self.logs["log_sim_config"] = pd.DataFrame(columns=
                                                    ["total_days"])
        self.logs["log_grid"] = ""
        
        self.aggregated_outputs = pd.DataFrame(columns=[
                                    "household", 
                                    globals_config.FGMEAT,
                                    globals_config.FGDAIRY,
                                    globals_config.FGVEGETABLE,
                                    globals_config.FGDRYFOOD,
                                    globals_config.FGSNACKS,
                                    globals_config.FGBAKED,
                                    globals_config.FGSTOREPREPARED,
                                    globals_config.FW_INEDIBLE,
                                    globals_config.FW_PLATE_WASTE,
                                    globals_config.FW_SPOILED,
                                    globals_config.STATUS_PREPARED,
                                    globals_config.STATUS_UNPREPARED,
                                    globals_config.STATUS_PREPREPARED,
                                    "n_quickcook",
                                    "n_cook",
                                    "n_leftovers",
                                    "n_shop",
                                    "n_quickshop"
                                    ])
    def log_grid(self,grid:"Grid"): # type: ignore
        """Write the current grid to the log_grid

        Args:
            grid (Grid): grid to log
        """        
        self.logs["log_grid"] = str(grid) # type: ignore
    def log_configs(self,houses:list["Household"]) -> None:  # type: ignore
        """Log the household configuration and simulation configurations.

        Args:
            houses (list[Household]): houses to log the information for
        """        
        
        
        self.logs["log_sim_config"].loc[0, "total_days"] = globals_config.SIMULATION_DAYS

        for house in houses: 
            self.logs["log_hh_config"].loc[int(house.id)] = { # type: ignore
                "household" :  int(house.id), 
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
                "shopping_frequency" : house.shopping_frequency
    }
            
    def log_households_daily(self,houses:list["Household"]) -> None: # type: ignore
        """Collects the daily data from each house passed in houses

        Args:
            houses (list[Household]): houses to log the information for
        """     
        for house in houses: 
            self.logs["log_hh_daily"].loc[len(self.logs["log_hh_daily"])] = { # type: ignore
                "household": int(house.id),
                "day":globals_config.DAY,
                "budget":house.shoppingManager.todays_budget,
                "servings":house.cookingManager.todays_servings,      
                "EEF": house.cookingManager.log_today_eef, 
                "cooked": house.cookingManager.log_today_cooked, 
                "ate_leftovers": house.cookingManager.log_today_leftovers,
                "quick_cook":house.cookingManager.log_today_quickcook,
                "shopping_time": house.log_shopping_time,
                "cooking_time": house.log_cooking_time
            }
    
    def log_households_left_resources(self, houses:list["Household"]) -> None:  # type: ignore
        """Tracks the final content of the storage, used after simulation is finished

        Args:
            houses (list[Household]): houses to log the information for
        """   
        for house in houses: 
            for storage in [house.fridge, house.pantry]:
                for i in storage.current_items.index:
                    item = storage.current_items.loc[i]
                    self.logs["log_still_have"].loc[len(self.logs["log_still_have"])] = { # type: ignore
                        "household": int(house.id),
                        "price": item["price"],
                        "servings": item["servings"],
                        "days_till_expiry": item["days_till_expiry"],
                        "status": item["status"],
                        globals_config.FGMEAT: item[globals_config.FGMEAT],
                        globals_config.FGDAIRY: item[globals_config.FGDAIRY],
                        globals_config.FGVEGETABLE: item[globals_config.FGVEGETABLE],
                        globals_config.FGDRYFOOD: item[globals_config.FGDRYFOOD],
                        globals_config.FGSNACKS: item[globals_config.FGSNACKS],
                        globals_config.FGBAKED: item[globals_config.FGBAKED],
                        globals_config.FGSTOREPREPARED: item[globals_config.FGSTOREPREPARED]
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
                    "day": globals_config.DAY,
                    'type': item["type"],
                    'servings': item["servings"],
                    'days_till_expiry': item["days_till_expiry"],
                    'price_per_serving': item["price_per_serving"],
                    'sale_type': item["sale_type"],
                    'discount_effect': item["discount_effect"],
                    'amount': item["amount"],
                    'sale_timer': item["sale_timer"],
                    'store': item["store"],
                    'product_ID':item["product_ID"]
                }
        
    
    def data_to_csv(self,logs_to_write: list[str]|None=None) -> None: 
        """Saves the finished tracked data to csv files

        Args:
            run (int): Number of simulation run, used to write folder_name
            logs_to_write (list[str] | None, optional): logs_to_write, None defaults to all logs in self.logs. Defaults to None.
        """                
        path = self._create_folder()
        
        if logs_to_write is not None and "aggregated_outputs" in logs_to_write:
            file_path = path + self.foldername + "//" + "aggregated_outputs" + ".csv"
            log_header = True
            if os.path.exists(file_path):
                log_header = False
            self.aggregated_outputs = self.aggregated_outputs.astype({col: "float64" for col in self.aggregated_outputs.columns.tolist()})
            self.aggregated_outputs = self.aggregated_outputs.round(3)
            self.aggregated_outputs.to_csv(file_path, header=log_header, mode="a", index=False)
            self.reset_logs()
        elif logs_to_write is not None: 
            for item in logs_to_write: 
                config_header = True
                config_path = path + self.foldername + f"//"+ item + ".csv"
                if os.path.exists(config_path):
                    config_header = False
                if isinstance(self.logs[item], pd.DataFrame):
                    self.logs[item].to_csv(config_path, header=config_header, mode="a", index=False)
                else: 
                    with open( config_path, "w", newline="") as file:
                        file.write(self.logs[item]) # type: ignore
        else:
            for log_name, log_file in self.logs.items():
                if not log_name == "log_hh_config" and not log_name == "log_sim_config"\
                    and not log_name == "log_grid":
                    file_path = path + self.foldername + "//" + log_name + ".csv"
                    log_header = True
                    if os.path.exists(file_path):
                        log_header = False
                    log_file.to_csv(file_path, header=log_header, mode="a", index=False)
                    self.reset_logs()
    
    def _create_folder(self)  -> str:
        """creates the folder name and returns it. Will be used for 
        all log files of that run. 

        Args:
            run (int): simulation run id, for folder creation

        Returns:
            str: foldername
        """        
        path = str(Path(__file__).parents[1])
        dt = datetime.datetime.now()
        if (not os.path.isdir(path + "//"+ globals_config.SIMULATION_OUTPUTFOLDER )): 
            os.mkdir(path + "//"+ globals_config.SIMULATION_OUTPUTFOLDER + "//")
        
        if globals_config.EXPERIMENT_NAME != None: 
            path = path + "//"+ globals_config.SIMULATION_OUTPUTFOLDER + "//" + globals_config.EXPERIMENT_NAME + "//"
            if (not os.path.isdir(path )): 
                os.mkdir(path)
        
        if self.foldername == "":
            if globals_config.SIMULATION_RUN != None: #either save by run id 
                self.foldername = "run_" + str(globals_config.SIMULATION_RUN)
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
            columns=["household","day","type","servings",
                    "days_till_expiry","price_per_serving","sale_type", "discount_effect", "amount", "sale_timer", "store", "product_ID"]),
        "log_eaten" : pd.DataFrame(
            columns=["household","day","price","servings","days_till_expiry","status",
                    globals_config.FGMEAT,globals_config.FGDAIRY,globals_config.FGVEGETABLE,globals_config.FGDRYFOOD,globals_config.FGSNACKS,globals_config.FGBAKED,
                    globals_config.FGSTOREPREPARED]),
        "log_still_have" : pd.DataFrame(
            columns=["household","price","servings","days_till_expiry","status",
                    globals_config.FGMEAT,globals_config.FGDAIRY,globals_config.FGVEGETABLE,globals_config.FGDRYFOOD,globals_config.FGSNACKS,globals_config.FGBAKED,
                    globals_config.FGSTOREPREPARED]),
        "log_wasted" : pd.DataFrame(
            columns=["household","day","price","servings","days_till_expiry","status","reason",
                    globals_config.FGMEAT,globals_config.FGDAIRY,globals_config.FGVEGETABLE,globals_config.FGDRYFOOD,globals_config.FGSNACKS,globals_config.FGBAKED,
                    globals_config.FGSTOREPREPARED]),
        "log_store_daily" : pd.DataFrame(
            columns=(["store","day","type","servings",
                    "days_till_expiry","price_per_serving","sale_type", "discount_effect", "amount", "sale_timer", "product_ID"])),
        "log_hh_daily" : pd.DataFrame(
            columns=["household","day","budget","servings","EEF","cooked","ate_leftovers","quick_cook","shopping_time", "cooking_time"])
        }
        
    def append_log(self, id:int, log_key:str, data:pd.DataFrame | pd.Series  | None ) -> None:
        """Adds new data to the log in self.log, defined by log_key

        Args:
            id (int): household id 
            log_key (str): string specifying which log to append the data to ["log_wasted", "log_eaten",
            "log_bought"]
            data (pd.DataFrame | pd.Series | None): data to be added

        Raises:
            ValueError: Wrong logging key has been passed
        """        
        if not data is None: 
            data_copy = data.copy()
            if isinstance(data_copy, pd.DataFrame):
                data_copy["household"] = id
                data_copy["day"] = globals_config.DAY
                
            else:
                data_copy = data_copy.to_frame().T
                data_copy["household"] = id
                data_copy["day"] = globals_config.DAY
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
            "day": globals_config.DAY,
            "servings": item["servings"],
            "days_till_expiry": item["days_till_expiry"],
            "status": item["status"],
            "price": item["price"],
            "reason":item["reason"],
            globals_config.FGMEAT: item[globals_config.FGMEAT],
            globals_config.FGDAIRY: item[globals_config.FGDAIRY],
            globals_config.FGVEGETABLE: item[globals_config.FGVEGETABLE],
            globals_config.FGDRYFOOD: item[globals_config.FGDRYFOOD],
            globals_config.FGSNACKS: item[globals_config.FGSNACKS],
            globals_config.FGBAKED: item[globals_config.FGBAKED],
            globals_config.FGSTOREPREPARED: item[globals_config.FGSTOREPREPARED]
        }
    def _log_eaten(self,data:pd.DataFrame) -> None:
        """adds data to the eaten log

        Args:
            data (pd.DataFrame): data to be added
        """  
        for _, item in data.iterrows():
            self.logs["log_eaten"].loc[len(self.logs["log_eaten"])] = { # type: ignore
            "household": item["household"],
            "day": globals_config.DAY,
            "price": item["price"],
            "servings": item["servings"],
            "days_till_expiry": item["days_till_expiry"],
            "status": item["status"],
            globals_config.FGMEAT: item[globals_config.FGMEAT],
            globals_config.FGDAIRY: item[globals_config.FGDAIRY],
            globals_config.FGVEGETABLE: item[globals_config.FGVEGETABLE],
            globals_config.FGDRYFOOD: item[globals_config.FGDRYFOOD],
            globals_config.FGSNACKS: item[globals_config.FGSNACKS],
            globals_config.FGBAKED: item[globals_config.FGBAKED],
            globals_config.FGSTOREPREPARED: item[globals_config.FGSTOREPREPARED]
        }
                
    def _log_bought(self,data:pd.DataFrame) -> None:
        """adds data to the bought log

        Args:
            data (pd.DataFrame): data to be added
        """  
        for _, item in data.iterrows():
            self.logs["log_bought"].loc[len(self.logs["log_bought"])] = { # type: ignore
                "household": item["household"],
                "day": globals_config.DAY,
                'type': item["type"],
                'servings': item["servings"],
                'days_till_expiry': item["days_till_expiry"],
                'price_per_serving': item["price_per_serving"],
                'sale_type': item["sale_type"],
                'discount_effect': item["discount_effect"],
                'amount': item["amount"],
                'sale_timer': item["sale_timer"],
                'store': item["store"],
                'product_ID':item["product_ID"]
            }
            
    def aggregate_outputs_daily(self, day:int, houses:list["Household"]): 
        #agg per household: 
        new_vals = {
                "household": -1,
                globals_config.FGMEAT: 0,
                globals_config.FGDAIRY: 0,
                globals_config.FGVEGETABLE: 0,
                globals_config.FGDRYFOOD: 0,
                globals_config.FGSNACKS: 0,
                globals_config.FGBAKED: 0,
                globals_config.FGSTOREPREPARED: 0,
                globals_config.FW_INEDIBLE: 0,
                globals_config.FW_PLATE_WASTE: 0,
                globals_config.FW_SPOILED: 0,
                globals_config.STATUS_PREPARED: 0,
                globals_config.STATUS_UNPREPARED: 0,
                globals_config.STATUS_PREPREPARED: 0,
                "n_quickcook": 0,
                "n_cook": 0,
                "n_leftovers": 0,
                "n_shop": 0,
                "n_quickshop": 0
            }
        
        for house in houses:       
            log_wasted = self.logs["log_wasted"]
            log_wasted = log_wasted[(log_wasted["day"] == day) & (log_wasted["household"] == house.id)]

            new_vals["household"] = house.id
            new_vals["n_quickcook"] = int(house.cookingManager.log_today_quickcook)
            new_vals["n_cook"] =  int(house.cookingManager.log_today_cooked)
            new_vals["n_leftovers"] = int(house.cookingManager.log_today_leftovers)
            new_vals["n_shop"] = int(house.log_shop)
            new_vals["n_quickshop"] = int(house.log_quickshop)
            
            if len(log_wasted) > 0:
                new_vals[globals_config.FGMEAT] = log_wasted[globals_config.FGMEAT].sum()
                new_vals[globals_config.FGDAIRY] = log_wasted[globals_config.FGDAIRY].sum()
                new_vals[globals_config.FGVEGETABLE] = log_wasted[globals_config.FGVEGETABLE].sum()
                new_vals[globals_config.FGDRYFOOD] = log_wasted[globals_config.FGDRYFOOD].sum()
                new_vals[globals_config.FGSNACKS] = log_wasted[globals_config.FGSNACKS].sum()
                new_vals[globals_config.FGBAKED] = log_wasted[globals_config.FGBAKED].sum()
                new_vals[globals_config.FGSTOREPREPARED] = log_wasted[globals_config.FGSTOREPREPARED].sum()
                
                new_vals[globals_config.FW_INEDIBLE] = self._sum_waste_per_reason(day,house.id,globals_config.FW_INEDIBLE)
                new_vals[globals_config.FW_PLATE_WASTE] = self._sum_waste_per_reason(day,house.id,globals_config.FW_PLATE_WASTE)
                new_vals[globals_config.FW_SPOILED] = self._sum_waste_per_reason(day,house.id,globals_config.FW_SPOILED)
                new_vals[globals_config.STATUS_PREPARED] = self._sum_waste_per_status(day, house.id,globals_config.STATUS_PREPARED)
                new_vals[globals_config.STATUS_UNPREPARED] = self._sum_waste_per_status(day, house.id,globals_config.STATUS_UNPREPARED)
                new_vals[globals_config.STATUS_PREPREPARED] = self._sum_waste_per_status(day, house.id,globals_config.STATUS_PREPREPARED)
                
            
            if house.id not in self.aggregated_outputs["household"].values: #init empty rows
                self.aggregated_outputs = pd.concat([self.aggregated_outputs, pd.DataFrame(new_vals, index=[0])], ignore_index=True)
            else: 
                new_vals["household"] = 0 #dont increment the id
                self.aggregated_outputs[self.aggregated_outputs["household"] == house.id] += pd.DataFrame(new_vals, index=[0]).iloc[0]
                
    def _sum_waste_per_reason(self,day:int, household:int, reason:str):
        log_wasted = self.logs["log_wasted"]
        log_wasted = log_wasted[(log_wasted["day"] == day) & (log_wasted["household"] == household) & (log_wasted["reason"] == reason)]
        if len(log_wasted) > 0:            
            return log_wasted[globals_config.FOOD_GROUPS["type"].values.tolist()].sum().sum()
        return 0
    
    def _sum_waste_per_status(self,day:int, household:int, status:str):
        log_wasted = self.logs["log_wasted"]
        log_wasted = log_wasted[(log_wasted["day"] == day) & (log_wasted["household"] == household) & (log_wasted["status"] == status)]
        if len(log_wasted) > 0:            
            return log_wasted[globals_config.FOOD_GROUPS["type"].values.tolist()].sum().sum()
        return 0