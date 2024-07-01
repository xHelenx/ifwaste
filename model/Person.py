import json
import logging
import random
from tkinter import N
import globals
from FoodGroups import FoodGroups

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
        - plate waste ratio 
        """                
        self.age = None
        self.gender = random.randint(globals.MALE, globals.FEMALE) #1 is female
        self.is_adult = None 
        self.kcal = None 
        self.susceptibility = None 
        self.concern = None
        self.plate_waste_ratio = None 
        
        food_groups = FoodGroups.get_instance()
        self.fg_preference = {item:random.uniform(0,1) for item in food_groups.get_all_food_groups()}
        self.req_servings = None 
        self.req_servings_per_fg = None 