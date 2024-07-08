import pandas as pd

from Food import Food

class Storage: 

    def __init__(self) -> None:
        self.current_items = pd.DataFrame(columns= [
            'type', 
            'servings', 
            'days_till_expiry'])
    
    def add(self, item:Food): 
        new_row = {"type" : item.type, "servings": item.servings, "days_till_expiry":item.days_till_expiry}
        self.current_items.loc[len(self.current_items)] = new_row
        
    
    def remove(self,item:Food):
        row_to_remove = self.current_items[(self.current_items["type"]==item.type) &\
            (self.current_items["servings"] == item.servings) &\
            (self.current_items["days_till_expiry"] == item.days_till_expiry)]
     
        self.current_items = self.current_items.drop(row_to_remove.index[0]) #just remove one row in case there are multiple
        
    def get_number_of_items(self):
        return len(self.current_items)
    
    def get_servings(self): 
        return self.current_items["servings"].sum()
    
    def get_servings_per_fg(self):
        return self.current_items.groupby("type")["servings"].sum()
    
    def get_earliest_expiry_date(self): 
        return self.current_items["days_till_expiry"].min()