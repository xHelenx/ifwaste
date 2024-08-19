import pandas as pd
import numpy as np

from FoodGroups import FoodGroups
import globals 
class Storage: 

    def __init__(self) -> None:
        self.current_items:pd.DataFrame = pd.DataFrame(columns= [
            globals.FGMEAT, 
            globals.FGDAIRY,
            globals.FGVEGETABLE, 
            globals.FGDRYFOOD,
            globals.FGBAKED,
            globals.FGSNACKS, 
            globals.FGSTOREPREPARED,
            'price',
            'status',
            'servings', 
            'days_till_expiry'])
        self.fg:FoodGroups = FoodGroups.get_instance() # type: ignore
    
    def add(self, item:pd.Series) -> None: 
        self.current_items.loc[len(self.current_items)] = item
        self.current_items.reset_index()
        
    
    def remove(self,item:pd.Series) -> None:
        row_to_remove = self.current_items[
            (self.current_items[globals.FGMEAT] == item[globals.FGMEAT] ) &
            (self.current_items[globals.FGDAIRY] == item[globals.FGDAIRY] ) &
            (self.current_items[globals.FGVEGETABLE] == item[globals.FGVEGETABLE] ) &
            (self.current_items[globals.FGDRYFOOD] == item[globals.FGDRYFOOD] ) &
            (self.current_items[globals.FGBAKED] == item[globals.FGBAKED] ) &
            (self.current_items[globals.FGSNACKS] == item[globals.FGSNACKS] ) &
            (self.current_items[globals.FGSTOREPREPARED] == item[globals.FGSTOREPREPARED]) &
            (self.current_items["price"] == item.price) &
            (self.current_items["status"] == item.status) &
            (self.current_items["servings"] == item.servings) &
            (self.current_items["days_till_expiry"] == item.days_till_expiry)]
     
        self.current_items = self.current_items.drop(row_to_remove.index[0]) #just remove one row in case there are multiple
        
    def get_item_by_strategy(self, strategy:str,preference_vector:dict[str,float]) -> pd.Series: 
       #default random
       #random" = choose random ingredients to cook wit
       #"EEF"    = choose "Earliest Expiration First" 
       
        assert not self.is_empty()
        
        
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
            idx = self.current_items['days_till_expiry'].idxmin()
            item = self.current_items.loc[idx]
            
        self.remove(item) # type: ignore
        return item      # type: ignore
    
   # def split_item()
    
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