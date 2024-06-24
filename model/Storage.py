import bisect
import random
import sys 

from Food import Food 

class Storage: 
    def __init__(self) -> None:
        self.current_items = []
        #self.capacity
    def get_item_by_strategy(self, strategy, food_type="any"): 
        """Returns an item based on a strategy and optionally a food type. 
        If there is no item matching these criteria none will be returned. 
        Returned items are removed from the storage

        Args:
            strategy (_type_): _description_
            food_type (str, optional): _description_. Defaults to "any".

        Returns:
            result (Food): food, might be none 
        """             
        if self.is_empty(): 
            return None 
        
        result = None
        if strategy == "EEF": 
            for item in self.current_items: 
                if item.type == food_type or food_type=="any": 
                    result = item 
        else: 
            if food_type != "any": 
                all_of_food_type = self._get_all_by_food_type(food_type)
                if all_of_food_type != []:
                    item = random.choice(all_of_food_type)    
                    result = item 
            else: 
                item = random.choice(self.current_items)
                result = item 
        
        if result != None: 
            self.current_items.remove(result)
        return result 
    
    def get_total_items(self): 
        return len(self.current_items)
    
    def get_total_servings(self): 
        servings = 0
        for item in self.current_items: 
            servings += item.servings 
        return servings 
    
    def get_total_kcal(self): 
        kcal = 0
        for item in self.current_items: 
            kcal += item.kcal_kg * item.kg
        return kcal 
    
    
    
    def get_earliest_expiry_date(self): 
        """Returns the expiry date of the first expiry item in storage

        Returns:
            expiry date (int): earliest expiry date
        """        
        if self.is_empty(): 
            return sys.maxsize 
        
        curr_exp = sys.maxsize
        for item in self.current_items: 
            if item.exp < curr_exp: 
                curr_exp = item.exp
                
        return curr_exp
    
    def _get_all_by_food_type(self, food_type): 
        """Returns all items, that match the food_type

        Args:
            food_type (str): food_type

        Returns:
            list[Food]: all items matching the food_type, not removed from storage!
        """        
        all_items = []
        for item in self.current_items: 
            if item.type == food_type: 
                all_items.append(item)
        return all_items
      
    def remove(self,item:Food):
        """Removes item from storage

        Args:
            item (Food): item to remove from storage
        """        
        self.current_items.remove(item)
        
    def add(self, item:Food): 
        """Adds item to storage sorted by expiry date. Ignores None items. 

        Args:
            item (Food): item to add
        """        
        if item != None: 
            bisect.insort(self.current_items, item)
        
    def debug_get_content(self) -> str: 
        """Debugging function to visualized the current content of a location (fridge, pantry)

        Args:
            location (list): Location to visualize content of

        Returns:
            str: string representing content of location
        """    
        debug_str = ""
        total_weight = 0
        for content in self.current_items: 
            debug_str += str(content) + "\n"
            total_weight += content.kg
        debug_str += "total: " + str(total_weight)
        return debug_str 
    
    def debug_get_weight(self) -> float: 
        total_weight = 0 
        for item in self.current_items: 
            total_weight += item.kg 
        return total_weight
    
    def is_empty(self): 
        return len(self.current_items) == 0
    