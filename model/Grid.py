from __future__ import annotations  # Delay import for type hints
from Store import Store
import math
import random
import globals
from Location import Location

class Grid: 
    def __init__(self) -> None:
        """Initalizes Neighborhood grid. 
        
        Attributes: 
            self.grid (list[list[tuple[int,int]) : 2d grid of the neighborhood identifying
            which location is at which coordinate (x,y)
            self.time_per_cell (float) : travel time required to travers a cell when planning the shortest way from a to b
            self.available_positions (list[tuple[int,int]]) : open spots for locations to be positioned on the grid
        """        
        gridsize = globals.NEIGHBORHOOD_HOUSES + sum(globals.NEIGHBORHOOD_STORE_AMOUNTS)
        #create grid that is as "square shaped as possible"      
        
        self.grid:list[list[tuple[int,int] | None | Location]] = self.setup_grid(gridsize=gridsize)    
        self.time_per_cell:float = globals.GRID_TRAVEL_TIME_PER_CELL
        self.available_positions:list[tuple[int,int]] =  [(r, c) for r in range(len(self.grid)) for c in range(len(self.grid[0]))]    
          
    def __str__(self) -> str:
        """Returns a string visualization of the grid.

        Returns:
            str: string representation of the grid
        """        
        from Household import Household
        from StoreDiscounterRetailer import StoreDiscounterRetailer
        from StorePremimumRetailer import StorePremimumRetailer
        from StoreConvenienceStore import StoreConvenienceStore
        grid_str = ""
        for i in range(len(self.grid))   :
            for j in range(len(self.grid[0])):
                if self.grid[i][j] is None:
                    grid_str += "NO,"
                elif isinstance(self.grid[i][j], Household):
                    grid_str += "HH-" + str(self.grid[i][j].id) + ","
                elif isinstance(self.grid[i][j], StoreDiscounterRetailer):
                    grid_str += "SD-" + str(self.grid[i][j].id) + ","
                elif isinstance(self.grid[i][j], StorePremimumRetailer):
                    grid_str += "SP-" +  str(self.grid[i][j].id) + ","
                elif isinstance(self.grid[i][j], StoreConvenienceStore):
                    grid_str += "SC-" + str(self.grid[i][j].id) + ","
                else: 
                    print(type(self.grid[i][j]))
                    grid_str += " ??"
            grid_str += "\n"
        return grid_str


    def get_coordinates(self,location:Location) -> tuple[int, int] : 
        """Returns x,y coordinate of the given location

        Args:
            location (Location): location to retrieve position for

        Raises:
            ValueError: Location does not exist in grid

        Returns:
            tuple[int, int]: x and y coordinate of the location
        """        
        for x in range(len(self.grid)): 
            for y in range(len(self.grid[0])):
                if self.grid[x][y] == location:
                    return (x,y)
        raise ValueError(f"Location {location.logger.name} not found in the grid.")
                
    def setup_grid(self, gridsize:int) -> list[list[None | tuple[int,int] | Location]]: 
        """Creates a grid depending on the gridsize. The grid is planned to be 
        as squared as possible offering a minimum of "gridsize" positions. 

        Args:
            gridsize (int): Required size of grid

        Returns:
            list[list[None | tuple[int,int]]]: 2d array reporesentation of grid
        """        
        sqrt_n = math.isqrt(gridsize)
        x_dim = sqrt_n
        
        while sqrt_n * x_dim < gridsize: 
            sqrt_n += 1 
            
        return [[None] * x_dim for _ in range(sqrt_n)]
    
    def assign_location(self, object:Location) -> None: 
        """Positions a location on a free position of the grid.

        Args:
            object (Location): object to place
        """        
        index = random.randint(0, len(self.available_positions) - 1)
        row, col = self.available_positions.pop(index)
        self.grid[row][col] = object
        
    def get_travel_time_one_way(self,start:tuple[int,int],destination:tuple[int,int]) -> float: 
        '''
        Returns the travel time from a to b (one way).
        
        Args: 
            start (tuple[int,int]): coordinate of starting position
            destination (tuple[int,int]): coordinate of destination
        Returns: 
            (float) : travel time in mins 
        '''
        return math.sqrt(math.pow((start[0]- destination[0]),2) + math.pow((start[1]- destination[1]),2)) * self.time_per_cell
    
    def get_travel_time_entire_trip(self, start:Location,stores:list[tuple[int,int]]):
        first_stop = stores[0]
        coords = self.get_coordinates(location=start)
        if len(stores) > 1:
            second_stop = stores[1]
            return self.get_travel_time_one_way(coords, first_stop) + self.get_travel_time_one_way(first_stop, second_stop) + self.get_travel_time_one_way(second_stop, coords) +\
            2 * globals.GRID_TIME_PER_STORE
        else:
            return self.get_travel_time_one_way(coords, first_stop) * 2 + globals.GRID_TIME_PER_STORE
  
    def get_stores_within_time_constraint(self,start:Location, avail_time:float) -> list[Store]: #assuming up to single travel 
        '''
        Returns a list of store options, that meet different criteria: 
                avail_time:  the traveling time for adding this store to the current trip does not exceed the avail time 
                avail_time considers travling to the first stop too, if not none
        
        Args: 
        start: location to start trip from
        avail_time: available traveling time 
        Returns: 
            (list[Store]) : a list of store options, for which all criteria are matching
        
        
        '''
        relevant_stores = []
      
        number_grids = int(avail_time/self.time_per_cell*2) #both ways included
        (x,y) = self.get_coordinates(location=start)
        
        x_min = x - number_grids
        if x_min < 0:
            x_min = 0
        y_min = y - number_grids
        if y_min < 0:
            y_min = 0
            
        x_max = x + number_grids
        if x_max > len(self.grid):
            x_max = len(self.grid)
        y_max = y + number_grids
        if y_max >= len(self.grid[0]):
            y_max = len(self.grid[0])
            
        for x_tmp in range(x_min,x_max):
            for y_tmp in range(y_min,y_max):
                if isinstance(self.grid[x_tmp][y_tmp], Store): 
                    stores = [(x_tmp,y_tmp)]
                    traveling_time = self.get_travel_time_entire_trip(start,stores) # type: ignore #we just go the other way round for easier calc
                    if traveling_time <= avail_time:
                        relevant_stores.append(self.grid[x_tmp][y_tmp])                    
        return relevant_stores
    
    def get_second_store_within_time_constraint(self,start:Location, first_stop:Store, avail_time:float, fg:list[str]|None=None, needs_lower_price:bool=False) -> list[Store]: #assuming up to single travel 
        '''
        Returns a list of store options, that meet different criteria: 
                avail_time:  the traveling time for adding this store to the current trip does not exceed the avail time 
                avail_time considers travling to the first stop too, if not none
            optional: 
                fg (str): the store must carry this food group XOR 
                needs_lower_price (bool): the store must be of a lower price than the "first stop" store
                first_stop (Store): required to set for needs_lower_price 
        
        Args: 
        start: location to start trip from
        avail_time: available traveling time 
        fg: food group that store has to offer 
        needs_lower_price: whether a store should be a lower price than (first_stop)
        
        Returns: 
            (list[Store]) : a list of store options, for which all criteria are matching
        '''
        relevant_stores = []                  
        first_stop_coord = self.get_coordinates(first_stop)
        price = first_stop.price
        for x_tmp in range(0,len(self.grid)):
            for y_tmp in range(0,len(self.grid[0])):
                if isinstance(self.grid[x_tmp][y_tmp], Store): 
                    if (x_tmp,y_tmp) != first_stop_coord: #dont add the same store again
                        stores = [first_stop_coord,(x_tmp,y_tmp)]
                        traveling_time = self.get_travel_time_entire_trip(start,stores) # type: ignore #we just go the other way round for easier calc
                        if traveling_time <= avail_time:
                            if not((fg != None and not
                                    set(fg).issubset(set(self.grid[x_tmp][y_tmp].get_available_food_groups()))) #type: ignore
                                   or (needs_lower_price and not self.grid[x_tmp][y_tmp].price < price)): #type: ignore
                                relevant_stores.append(self.grid[x_tmp][y_tmp])
                        
        return relevant_stores
    