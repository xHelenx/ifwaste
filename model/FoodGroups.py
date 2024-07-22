import json
import pandas as pd
import globals 

class FoodGroups(): 
    _instance = None  
    
    def __init__(self) -> None:
        if not FoodGroups._instance: 
            with open(globals.CONFIG_PATH) as f: 
                config = json.load(f)  
                
                food_groups = []
                for _, value in config["Food"].items(): 
                    food_groups.append({
                        'type': value['type'],
                        'kg_per_serving': value['kg_per_serving'],
                        'kcal_per_kg': value['kcal_per_kg'],
                        'inedible_percentage': value['inedible_percentage'],
                        'exp_min': value['exp_min'],
                        'exp_max': value['exp_max']
                    })
                self.food_groups = food_groups
                FoodGroups._instance = self
                
            self.food_groups = pd.DataFrame(food_groups)
        
        
    @staticmethod   
    def get_instance(): 
        if not FoodGroups._instance:
            FoodGroups()
        return FoodGroups._instance 
    
    def get_food_group(self, name:str) -> str:
        return self.food_groups[self.food_groups['type'] == name]
        
    def get_all_food_groups(self) -> list:
        return self.food_groups["type"]