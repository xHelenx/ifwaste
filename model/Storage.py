import pandas as pd
import numpy as np
import globals_config as globals_config 
class Storage: 

    def __init__(self) -> None:
        """Initializes a Storage
        
        Class Variables: 
            current_items (pd.DataFrame): Items that are currently held in the storage space
            
        """    
        self.current_items: pd.DataFrame = pd.DataFrame(
            columns=[
                globals_config.FGMEAT, 
                globals_config.FGDAIRY,
                globals_config.FGVEGETABLE, 
                globals_config.FGDRYFOOD,
                globals_config.FGSNACKS, 
                globals_config.FGBAKED,
                globals_config.FGSTOREPREPARED,
                'price',
                'status',
                'servings', 
                'days_till_expiry',
                'inedible_percentage'
            ],
        )
        self.current_items[globals_config.FGMEAT] = self.current_items[globals_config.FGMEAT].astype(float)
        self.current_items[globals_config.FGDAIRY] = self.current_items[globals_config.FGDAIRY].astype(float)
        self.current_items[globals_config.FGVEGETABLE] = self.current_items[globals_config.FGVEGETABLE].astype(float)
        self.current_items[globals_config.FGDRYFOOD] = self.current_items[globals_config.FGDRYFOOD].astype(float)
        self.current_items[globals_config.FGBAKED] = self.current_items[globals_config.FGBAKED].astype(float)
        self.current_items[globals_config.FGSNACKS] = self.current_items[globals_config.FGSNACKS].astype(float)
        self.current_items[globals_config.FGSTOREPREPARED] = self.current_items[globals_config.FGSTOREPREPARED].astype(float)
        
        self.current_items['price'] = self.current_items['price'].astype(float)
        self.current_items['status'] = self.current_items['status'].astype(str)
        self.current_items['servings'] = self.current_items['servings'].astype(int)
        self.current_items['days_till_expiry'] = self.current_items['days_till_expiry'].astype(int)  
        self.current_items['inedible_percentage'] = self.current_items['inedible_percentage'].astype(float)  

    def add(self, item: pd.Series) -> None: 
        """Adds the item to the storage

        Args:
            item (pd.Series): item to be added
        """        
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
        """Removes item from storage 

        Args:
            item (pd.Series): item to be removed
        """                
        mask = np.all([
            np.isclose(self.current_items[col], item[col], equal_nan=True) if pd.api.types.is_float_dtype(self.current_items[col]) 
            else (self.current_items[col] == item[col])
            for col in item.index
            ], axis=0)
        
        matching_indices = self.current_items[mask].index
        if len(matching_indices) > 0:
                # Remove only the first match 
                self.current_items = self.current_items.drop(matching_indices[0])
    
    def get_item_by_strategy(self, strategy:str,preference_vector:dict[str,float], food_groups:list=[]) -> pd.Series|None: 
        """Retrieves an item from storage depending on the strategy. The likelihood of an item being of a specific food group 
        furthermore depends on the the given preference vector

        Args:
            strategy (str): Strategy that is used to select an item from the storage, either "random" or "EEF" (earliest expiration first)
            preference_vector (dict[str,float]): dictionary mapping the food groups (str) to their preference (0-1), defines the likelihood
            to select an item given a food group

        Returns:
            pd.Series|None: item selected for return
        """        
        if food_groups == []: 
            food_groups = globals_config.FOOD_GROUPS["type"].to_list()
        if self.is_empty(): 
            return None 
        
        for fg in food_groups: 
            if preference_vector[fg] <= 0:
                food_groups.remove(fg)  # Remove food groups with zero preference        
        
        rel_items = self.current_items[self.current_items[food_groups].gt(0).any(axis=1)]
        if len(rel_items) == 0:
            return None #e.g. in quickshop maybe some fg are used up during sampling a.s.p
        
        if strategy == "random": 
            #random grab 
            fgs = list(preference_vector.keys())
            weights = rel_items[fgs].dot(pd.Series(preference_vector))
            weights = weights / weights.sum()
            weights = weights.astype(np.float64)
            #weighted sample
            idx = np.random.choice(rel_items.index, size=1, replace=False, p=weights.values)
            item = rel_items.loc[idx].iloc[0]
            #if item == None: #there are items but not of the preferred fg / so well just grab something to cook with
            #    item = np.random.sample(self.pantry.current_items)
                
        else: #EEF
            idx = rel_items['days_till_expiry'].astype(float).idxmin()
            item = rel_items.loc[idx]
            
        self.remove(item) # type: ignore
        return item      # type: ignore
    
    
    def get_total_servings(self) -> float: 
        """Returns the total amount of servings, that is held in this storage

        Returns:
            float: _description_
        """        
        if len(self.current_items) == 0:
            return 0
            
        return self.current_items["servings"].sum()
    
    def get_servings_per_fg(self) -> pd.Series:
        """Returns the total amount of servings per food group, that is held
        in this storage

        Returns:
            pd.Series: Series that maps food group to number of servings
        """        
        fgs = globals_config.FOOD_GROUPS["type"].to_list()
        result = pd.Series(dict(zip(fgs, [0]*len(fgs))))
        
        return self.current_items[fgs].sum()
            
    
    def is_empty(self) -> bool: 
        """Returns whether the storage is empty

        Returns:
            bool: indicates if the storage is empty
        """        
        return self.current_items.empty
    def get_earliest_expiry_date(self) -> int: 
        """Returns the earliest expiry date in the storage space

        Returns:
            int: earliest expiry date in days
        """        
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