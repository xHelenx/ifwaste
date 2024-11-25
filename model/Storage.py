import pandas as pd
import numpy as np
from param import DataFrame

from FoodGroups import FoodGroups
import globals 
class Storage: 

    def __init__(self) -> None:
        self.current_items: pd.DataFrame = pd.DataFrame(
            columns=[
                globals.FGMEAT, 
                globals.FGDAIRY,
                globals.FGVEGETABLE, 
                globals.FGDRYFOOD,
                globals.FGSNACKS, 
                globals.FGBAKED,
                globals.FGSTOREPREPARED,
                'price',
                'status',
                'servings', 
                'days_till_expiry',
                'inedible_percentage'
            ],
        )
        self.current_items[globals.FGMEAT] = self.current_items[globals.FGMEAT].astype(float)
        self.current_items[globals.FGDAIRY] = self.current_items[globals.FGDAIRY].astype(float)
        self.current_items[globals.FGVEGETABLE] = self.current_items[globals.FGVEGETABLE].astype(float)
        self.current_items[globals.FGDRYFOOD] = self.current_items[globals.FGDRYFOOD].astype(float)
        self.current_items[globals.FGBAKED] = self.current_items[globals.FGBAKED].astype(float)
        self.current_items[globals.FGSNACKS] = self.current_items[globals.FGSNACKS].astype(float)
        self.current_items[globals.FGSTOREPREPARED] = self.current_items[globals.FGSTOREPREPARED].astype(float)
        
        self.current_items['price'] = self.current_items['price'].astype(float)
        self.current_items['status'] = self.current_items['status'].astype(str)
        self.current_items['servings'] = self.current_items['servings'].astype(int)
        self.current_items['days_till_expiry'] = self.current_items['days_till_expiry'].astype(int)  
        self.current_items['inedible_percentage'] = self.current_items['inedible_percentage'].astype(float)  

        self.fg: FoodGroups = FoodGroups.get_instance()  # type: ignore

    def add(self, item: pd.Series) -> None: 
        if self.current_items.empty:
            self.current_items = pd.DataFrame(columns=list(item.keys()))

        # Convert item to a DataFrame and concatenate
        item_df = pd.DataFrame([item])
        
        if len(self.current_items) == 0:
                    self.current_items = item_df
        else:
            self.current_items = pd.concat([self.current_items, item_df], ignore_index=True)
        self.current_items.reset_index(drop=True, inplace=True)


    def remove(self, item: pd.Series) -> None:            
        mask = np.all([
            np.isclose(self.current_items[col], item[col], equal_nan=True) if pd.api.types.is_float_dtype(self.current_items[col]) 
            else (self.current_items[col] == item[col])
            for col in item.index
            ], axis=0)
        
        matching_indices = self.current_items[mask].index
        if len(matching_indices) > 0:
                # Remove only the first match 
                self.current_items = self.current_items.drop(matching_indices[0])
    
    def get_item_by_strategy(self, strategy:str,preference_vector:dict[str,float]) -> pd.Series|None: 
       #default random
       #random" = choose random ingredients to cook wit
       #"EEF"    = choose "Earliest Expiration First" 
       
        if self.is_empty(): 
            return None 
        
        if strategy == None or strategy == "random": 
            #random grab 
            fgs = list(preference_vector.keys())
            weights = self.current_items[fgs].dot(pd.Series(preference_vector))
            weights = weights / weights.sum()
            weights = weights.astype(np.float64)
            #weighted sample
            idx = np.random.choice(self.current_items.index, size=1, replace=False, p=weights.values)
            item = self.current_items.loc[idx].iloc[0]
            
        else: #EEF
            idx = self.current_items['days_till_expiry'].astype(float).idxmin()
            item = self.current_items.loc[idx]
            
        self.remove(item) # type: ignore
        return item      # type: ignore
    
    def get_number_of_items(self) -> int:
        return len(self.current_items)
    
    def get_total_servings(self) -> float: 
        if len(self.current_items) == 0:
            return 0
            
        return self.current_items["servings"].sum()
    
    def get_servings_per_fg(self) -> pd.Series:
        fgs = self.fg.get_all_food_groups()
        result = pd.Series(dict(zip(fgs, [0]*len(fgs))))
        
        return self.current_items[fgs].sum()
            
    
    def is_empty(self) -> bool: 
        return self.current_items.empty
    def get_earliest_expiry_date(self) -> int: 
        return self.current_items["days_till_expiry"].min()
    
    def debug_get_content(self) -> str: 
        """Debugging function to visualized the current content of a location (fridge, pantry)

        Args:
            location (list): Location to visualize content of

        Returns:
            str: string representing content of location
        """    
        debug_str = ""
        total_weight = 0
        if len(self.current_items) > 0:
            for idx,row in self.current_items.iterrows(): 
                debug_str += str(row) + "\n"
                total_weight += row["servings"]
            debug_str += "total: " + str(total_weight)
        return debug_str