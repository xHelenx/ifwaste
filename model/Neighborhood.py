
import math
import random
from DataLogger import DataLogger
from Household import Household
from Store import Store
import pandas as pd
import globals 


class Neighborhood():
    def __init__(self):
        """Initializes the neighborhood, by assigning the store to the houses 
        and setting up logging 

        """  
        self.stores = []
        self.houses = []
        
        
        self.grid = self.get_grid(gridsize)
        available_positions = [(r, c) for r in range(self.grid) for c in range(self.grid[0])]      
              
        #setup all stores
        for store in globals.NEIGHBORHOOD_STORE_TYPE:
            for i in range (0,globals.NEIGHBORHOOD_STORE_AMOUNTS): 
                location = self.assign_location(available_positions)
                store = Store(globals.NEIGHBORHOOD_STORE_TYPE, location)
                self.store.append(store)

        
        #setup all households
        assert globals.NEIGHBORHOOD_HOUSES >= globals.NEIGHBORHOOD_SERVING_BASED 
        for i in range(0,globals.NEIGHBORHOOD_SERVING_BASED): 
            location = self.assign_location(available_positions)
            house = Household(i,location,is_serving_based=True)
            self.houses.append(house)
        for i in range(globals.NEIGHBORHOOD_SERVING_BASED,globals.NEIGHBORHOOD_HOUSES): 
            location = self.assign_location(available_positions)
            house = Household(i,location,is_serving_based=False)
        
        #setup datalogger
        self.data_logger = DataLogger()
        
    def run(self, days= 365):
        """Runs the simulation for the amount of days specified

        Args:
            days (int, optional): number of days to simulate. Defaults to 365.
        """        
        for i in range(days):
            print(i)
            for house in self.houses:
                house.do_a_day(day=i)
                self.data_logger.log_households_daily(houses=house, day=i)
            
        self.data_logger.log_households_left_resources(house=house, day=i)
        
        

    