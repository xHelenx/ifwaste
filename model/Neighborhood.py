
from DataLogger import DataLogger
from Household import Household
import globals 
from Grid import Grid
from StoreLowTier import StoreLowTier 
from StoreMidTier import StoreMidTier
from Store import Store
from EnumStoreTier import EnumStoreTier 

class Neighborhood():
    def __init__(self) -> None:
        """Initializes the neighborhood, by assigning the store to the houses 
        and setting up logging 

        """  
        self.stores:list[Store] = []
        self.houses:list[Household] = []
        
        self.grid = Grid()
        #setup datalogger
        
        self.data_logger:DataLogger = DataLogger()
        #setup all stores
        for i in range(len(globals.NEIGHBORHOOD_STORE_TYPES)):
            for j in range (0,globals.NEIGHBORHOOD_STORE_AMOUNTS[i]): 
                if globals.NEIGHBORHOOD_STORE_TYPES[i] == EnumStoreTier.LOWTIER.name:
                    store = StoreLowTier(store_type=EnumStoreTier.LOWTIER, grid=self.grid,id=i*j+j)
                elif globals.NEIGHBORHOOD_STORE_TYPES[i] == EnumStoreTier.MIDTIER.name:
                    store = StoreMidTier(store_type=EnumStoreTier.MIDTIER, grid=self.grid,id=i*j+j)
                else: 
                    raise ValueError("store type does not exist")
                self.grid.assign_location(object=store)
                self.stores.append(store)

        
        #setup all households
        assert globals.NEIGHBORHOOD_HOUSES >= globals.NEIGHBORHOOD_SERVING_BASED 
        for i in range(0,globals.NEIGHBORHOOD_SERVING_BASED): 
            house = Household(id=i,grid=self.grid,datalogger=self.data_logger,is_serving_based=True)
            self.grid.assign_location(object=house)
            self.houses.append(house)
        for i in range(globals.NEIGHBORHOOD_SERVING_BASED,globals.NEIGHBORHOOD_HOUSES): 
            house = Household(id=i,grid=self.grid,datalogger=self.data_logger,is_serving_based=False)
            self.grid.assign_location(object=house)
            self.houses.append(house)
        
        
    def run(self, days= 365, run_id=None) -> None:
        """Runs the simulation for the amount of days specified

        Args:
            days (int, optional): number of days to simulate. Defaults to 365.
        """        
        self.data_logger.log_households_config(houses=self.houses)
        self.data_logger.data_to_csv(experiment_name=globals.EXPERIMENT_NAME, run=run_id, write_only_config=True)
        for i in range(days):
            print(i)
              
            #for store in self.stores: 
                #TODO store.do_a_day()
                
            #TODO add random order
            for house in self.houses:
                house.do_a_day(day=i)
                
            #TODO is order relevant?    
            self.data_logger.log_households_daily(houses=self.houses, day=i)
            self.data_logger.log_stores_daily(stores=self.stores, day=i)
            if i%globals.SIMULATION_WRITE_TO_FILE_INTERVAL == 0: 
                self.data_logger.data_to_csv(experiment_name=globals.EXPERIMENT_NAME, run=run_id, write_only_config=False)
    
        self.data_logger.log_households_left_resources(houses=self.houses)
        
        

    