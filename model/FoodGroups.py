from __future__ import annotations
import json
import pandas as pd
import globals 

class FoodGroups(): 
    _instance = None
        
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FoodGroups, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        """Initializes FoodGroup class

        Attributes: 
            self.foodgroups (pd.Dataframe): holds all static information about each food group
        """        
        if not hasattr(self, 'initialized'):  # Ensure initialization happens only once
            try:
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
                    self.food_groups:pd.DataFrame = pd.DataFrame(food_groups)
                    self.initialized:bool = True  # Mark as initialized
            except FileNotFoundError:
                raise RuntimeError(f"Configuration file {globals.CONFIG_PATH} not found.")
            except json.JSONDecodeError:
                raise RuntimeError(f"Error decoding JSON from {globals.CONFIG_PATH}.")
            except KeyError as e:
                raise RuntimeError(f"Missing expected key in configuration file: {e}")
    
    @staticmethod   
    def get_instance() -> FoodGroups:  
        """Returns FoodGroup instance

        Returns:
            fg (FoodGroup): FoodGroups instance
        """        
        if not FoodGroups._instance:
            FoodGroups()
        return FoodGroups._instance  # type: ignore
    
    def get_food_group(self, name:str) -> pd.DataFrame:
        """Returns a Dataframe with information about one fg

        Args:
            name (str): fg to retrieve information about

        Returns:
            pd.DataFrame: information about fg
        """        
        return self.food_groups[self.food_groups['type'] == name]
        
    def get_all_food_groups(self) -> list[str]:
        """Returns a list of all food groups as a str

        Returns:
            list[str]: List of food groups
        """        
        return self.food_groups["type"].tolist()