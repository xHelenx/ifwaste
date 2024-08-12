import pandas as pd

from Food import Food
from FoodGroups import FoodGroups

class Storage: 

    def __init__(self) -> None:
        self.current_items:pd.DataFrame = pd.DataFrame(columns= [
            'type', 
            'servings', 
            'days_till_expiry'])
        self.fg:FoodGroups = FoodGroups.get_instance() # type: ignore
    
    def add(self, item:Food) -> None: 
        new_row = {"type" : item.type, "servings": item.servings, "days_till_expiry":item.days_till_expiry}
        self.current_items.loc[len(self.current_items)] = new_row # type: ignore
        
    
    def remove(self,item:Food) -> None:
        row_to_remove = self.current_items[(self.current_items["type"]==item.type) &\
            (self.current_items["servings"] == item.servings) &\
            (self.current_items["days_till_expiry"] == item.days_till_expiry)]
     
        self.current_items = self.current_items.drop(row_to_remove.index[0]) #just remove one row in case there are multiple
        
    def get_number_of_items(self) -> int:
        return len(self.current_items)
    
    def get_total_servings(self) -> float: 
        if len(self.current_items) == 0:
            return 0
            
        return self.current_items["servings"].sum()
    
    def get_servings_per_fg(self) -> pd.Series:
        fgs = self.fg.get_all_food_groups()
        result = pd.Series(dict(zip(fgs, [0]*len(fgs))))
        
        for fg in fgs: 
            servings_fg = self.current_items[self.current_items["type"] ==fg]["servings"].sum()
            if servings_fg != None: 
                result[fg] = 0
            else:
                result[fg] = servings_fg
            
        return result      
    
    def is_empty(self) -> bool: 
        return self.current_items.empty
    def get_earliest_expiry_date(self) -> int: 
        return self.current_items["days_till_expiry"].min()
    
    def get_total_kcal(self) -> float: 
        #to dict
        food_groups_dict = self.fg.food_groups.set_index('type').to_dict(orient='index')
        #group by 'type' and sum 'servings'
        grouped_items = self.current_items.groupby('type', as_index=False).agg({'servings': 'sum'})
        
        #calc kcals
        total_kcal = 0
        for _, row in grouped_items.iterrows():
            food_type = row['type']
            servings = row['servings']
            
            if food_type in food_groups_dict:
                food_data = food_groups_dict[food_type]
                kcal_per_serving = servings * food_data['kg_per_serving'] * food_data['kcal_per_kg']
                total_kcal += kcal_per_serving
        
        return total_kcal
    
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