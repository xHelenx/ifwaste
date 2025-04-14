
import random
from DataLogger import DataLogger
from Household import Household
import globals 
from Grid import Grid
from StoreDiscounterRetailer import StoreDiscounterRetailer 
from StorePremimumRetailer import StorePremimumRetailer
from StoreConvenienceStore import StoreConvenienceStore 
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
        for i in range(len(globals.NH_STORE_TYPES)):
            for j in range (0,globals.NH_STORE_AMOUNTS[i]): 
                if globals.NH_STORE_TYPES[i] == EnumStoreTier.DISCOUNTRETAILER.value:
                    store = StoreDiscounterRetailer(grid=self.grid,id=i*j+j)
                elif globals.NH_STORE_TYPES[i] == EnumStoreTier.PREMIUMTIER.value:
                    store = StorePremimumRetailer(grid=self.grid,id=i*j+j)
                elif globals.NH_STORE_TYPES[i] == EnumStoreTier.CONVENIENCETIER.value:
                    store = StoreConvenienceStore(grid=self.grid,id=i*j+j)
                else: 
                    raise ValueError("store type does not exist")
                self.grid.assign_location(object=store)
                self.stores.append(store)

        
        #setup all households
        for i in range(0,globals.NH_HOUSES): 
            house = Household(id=i,grid=self.grid,datalogger=self.data_logger)
            self.grid.assign_location(object=house)
            self.houses.append(house)
        
        
    def run(self, run_id:int) -> None:
        """Runs the simulation for the amount of days specified

        Args:
            days (int, optional): number of days to simulate. Defaults to 365.
        """        
        self.data_logger.log_configs(houses=self.houses)
        self.data_logger.log_grid(grid=self.grid)
        self.data_logger.data_to_csv(run=run_id, logs_to_write=["log_hh_config", "log_sim_config", "log_grid"])
        globals.DAY = 0
        for i in range(globals.SIMULATION_DAYS):
            print(i)
            #store restock / sales 
            for store in self.stores: 
                store.do_before_day()
                
            random.shuffle(self.houses) #increase fairness, that not always the same household goes shopping last (might be out of stock)
            for house in self.houses:
                house.do_a_day()
                left = house.pantry.current_items["servings"].sum() + house.fridge.current_items["servings"].sum() 
                #globals.log(house,"LEFT: %i", left)
                
            #stock decays / throw out items 
            for store in self.stores: 
                store.do_after_day()

            self.data_logger.log_households_daily(houses=self.houses)
            self.data_logger.log_stores_daily(stores=self.stores)
            if i%globals.SIMULATION_WRITE_TO_FILE_INTERVAL == 0: 
                self.data_logger.data_to_csv(run=run_id) #TODO make sure rest is written depenidng on %

            
            globals.DAY += 1
            
        self.data_logger.log_households_left_resources(houses=self.houses)
        self.data_logger.data_to_csv(run=run_id, logs_to_write=["log_still_have"])

        #unregister logger
        for house in self.houses: 
            house.unregister_logger()
        for store in self.stores:
            store.unregister_logger()
        

    