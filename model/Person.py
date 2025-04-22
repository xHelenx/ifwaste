import json
import logging
import random
from tkinter import N
import globals

class Person():
    def __init__(self):
        """Initializes an adult person by:
        - age 
        - gender
        - kcal = kcal required per day
        - susceptibility = susceptibility to other opinions about economical, environmental and health concern
        within the household
        - concern = list of concern [env,eco,health], value between 0-1, 1 indicating a high concern
        - req_serving = requried servings per food type 
        - plate waste ratio: percentage of food that is left on the place (0-1)
        - fg_preference: indicates the preference (0-1) for each food group
        
        """                
        self.gender:int = random.randint(globals.MALE, globals.FEMALE) #1 is female
        self.is_adult:bool 
        self.kcal:float
        self.susceptibility:float
        self.concern:list[float]
        self.plate_waste_ratio :float 
        
        self.fg_preference:dict[str,float] = {item:random.uniform(0,1) for item in globals.FOOD_GROUPS["type"].to_list()}
        self.req_servings: float 
        self.req_servings_per_fg:dict[str,float] 