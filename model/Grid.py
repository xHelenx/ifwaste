from __future__ import annotations  # Delay import for type hints
from Store import Store
import math
import random
import globals
from Location import Location

class Grid: 
    def __init__(self) -> None:
        gridsize = globals.NEIGHBORHOOD_HOUSES + sum(globals.NEIGHBORHOOD_STORE_AMOUNTS)
        #create grid that is as "square shaped as possible"      
        
        self.grid:list[list[tuple[int,int] | None]] = self.setup_grid(gridsize=gridsize)    
        self.time_per_cell:float = globals.GRID_TRAVEL_TIME_PER_CELL
        self.available_positions:list[tuple[int,int]] =  [(r, c) for r in range(len(self.grid)) for c in range(len(self.grid[0]))]    
          
    def __str__(self) -> str:
        from Household import Household
        from StoreLowTier import StoreLowTier
        from StoreMidTier import StoreMidTier
        from StoreConvenientStore import StoreConvenientStore
        grid_str = ""
        for i in range(len(self.grid))   :
            for j in range(len(self.grid[0])):
                if self.grid[i][j] is None:
                    grid_str += " -"
                elif isinstance(self.grid[i][j], Household):
                    grid_str += " h "
                elif isinstance(self.grid[i][j], StoreLowTier):
                    grid_str += " sl"
                elif isinstance(self.grid[i][j], StoreMidTier):
                    grid_str += " sm"
                elif isinstance(self.grid[i][j], StoreConvenientStore):
                    grid_str += " sc"
                else: 
                    print(type(self.grid[i][j]))
                    grid_str += " ??"
            grid_str += "\n"
        return grid_str

    def get_coordinates(self,location:Location) -> tuple[int, int] : 
        for x in range(len(self.grid)): 
            for y in range(len(self.grid[0])):
                if self.grid[x][y] == location:
                    return (x,y)
        raise ValueError(f"Location {location} not found in the grid.")
                
    def setup_grid(self, gridsize:int) -> list[list[None | tuple[int,int]]]: 
        sqrt_n = math.isqrt(gridsize)
        x_dim = sqrt_n
        
        while sqrt_n * x_dim < gridsize: 
            sqrt_n += 1 
            
        return [[None] * x_dim for _ in range(sqrt_n)]
    
    def assign_location(self, object) -> None: 
        index = random.randint(0, len(self.available_positions) - 1)
        row, col = self.available_positions.pop(index)
        self.grid[row][col] = object
        
    def get_travel_time_one_way(self,start:tuple[int,int],destination:tuple[int,int]) -> float: 
        '''
        1x travel distance
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
  
    def get_stores_within_time_constraint(self,start:Location, avail_time:float, fg:str | None=None, needs_lower_tier:bool=False, first_stop: Store | None=None) -> list[Store]: #assuming up to single travel 
        '''
        start and stops are stores/households
        
        if fg is missing -> add fg param
        if needs lowertier store -> needs_lower_tier = True, first_stop = entry
        
        not fg and lower_tier at the same time 
        
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
            
        first_location = None
        if first_stop != None:
            first_location = self.get_coordinates(location=first_stop)
            if needs_lower_tier:
                tier = first_stop.store_type.tier
        for x_tmp in range(x_min,x_max):
            for y_tmp in range(y_min,y_max):
                if isinstance(self.grid[x_tmp][y_tmp], Store): 
                    stores = [(x_tmp,y_tmp)]
                    if first_location != None:
                        stores.append(first_location)
                    traveling_time= self.get_travel_time_entire_trip(start,stores) # type: ignore #we just go the other way round for easier calc
                    
                    if traveling_time <= avail_time:
                        if fg != None: #we need to find a store that offers a specifc fg
                            if self.grid[x_tmp][y_tmp].is_fg_in_productrange(fg): # type: ignore
                                relevant_stores.append(self.grid[x_tmp][y_tmp])
                        elif needs_lower_tier:
                            if self.grid[x_tmp][y_tmp].store_type.tier < tier: # type: ignore
                                relevant_stores.append(self.grid[x_tmp][y_tmp])
                        else:
                            relevant_stores.append(self.grid[x_tmp][y_tmp])
                    
        return relevant_stores
    