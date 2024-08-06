
from DataLogger import DataLogger
from Household import Household
import globals 
from Grid import Grid
from StoreLowTier import StoreLowTier 
from StoreMidTier import StoreMidTier
from EnumStoreTier import EnumStoreTier 

class Neighborhood():
    def __init__(self):
        """Initializes the neighborhood, by assigning the store to the houses 
        and setting up logging 

        """  
        self.stores = []
        self.houses = []
        self.grid = Grid()
              
        #setup all stores
        for i in range(len(globals.NEIGHBORHOOD_STORE_TYPES)):
            for j in range (0,globals.NEIGHBORHOOD_STORE_AMOUNTS[i]): 
                if globals.NEIGHBORHOOD_STORE_TYPES[i] == EnumStoreTier.LOWTIER.name:
                    store = StoreLowTier(EnumStoreTier.LOWTIER, self.grid,i*j+j)
                elif globals.NEIGHBORHOOD_STORE_TYPES[i] == EnumStoreTier.MIDTIER.name:
                    store = StoreMidTier(EnumStoreTier.MIDTIER, self.grid,i*j+j)
                else: 
                    raise ValueError("store type does not exist")
                self.grid.assign_location(store)
                self.stores.append(store)

        
        #setup all households
        assert globals.NEIGHBORHOOD_HOUSES >= globals.NEIGHBORHOOD_SERVING_BASED 
        for i in range(0,globals.NEIGHBORHOOD_SERVING_BASED): 
            house = Household(i,self.grid,is_serving_based=True)
            self.grid.assign_location(house)
            self.houses.append(house)
        for i in range(globals.NEIGHBORHOOD_SERVING_BASED,globals.NEIGHBORHOOD_HOUSES): 
            house = Household(i,self.grid,is_serving_based=False)
            self.grid.assign_location(house)
            self.houses.append(house)
        
        #setup datalogger
        self.data_logger = DataLogger()
        
    def run(self, days= 365):
        """Runs the simulation for the amount of days specified

        Args:
            days (int, optional): number of days to simulate. Defaults to 365.
        """        
        self.data_logger.log_households_config(houses=self.houses)
        for i in range(days):
            print(i)
              
            #for store in self.stores: 
                #TODO store.do_a_day()
                
            #TODO add random order
            for house in self.houses:
                house.do_a_day(day=i)
                
            #TODO is order relevant?    
            self.data_logger.log_households_daily(house=self.houses, day=i)
            self.data_logger.log_stores_daily(store=self.stores, day=i)
            
        self.data_logger.log_households_left_resources(house=house, day=i)
        
        

    