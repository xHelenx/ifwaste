from xmlrpc.client import boolean
from Store import Store
import math
import random
import globals


class Grid: 
    def __init__(self) -> None:
        gridsize = globals.NEIGHBORHOOD_HOUSES + sum(globals.NEIGHBORHOOD_STORE_AMOUNTS)
        #create grid that is as "square shaped as possible"      
        
        self.grid = self.get_grid(gridsize)    
        self.time_per_cell = globals.GRID_TRAVEL_TIME_PER_CELL
        self.available_positions =  [(r, c) for r in range(len(self.grid)) for c in range(len(self.grid[0]))]    
          
    def __str__(self) -> str:
        from Household import Household
        from StoreLowTier import StoreLowTier
        from StoreMidTier import StoreMidTier
        grid_str = ""
        for i in range(len(self.grid))   :
            for j in range(len(self.grid[0])):
                if self.grid[i][j] == None:
                    grid_str += " -"
                if isinstance(self.grid[i][j], Household):
                    grid_str += " h "
                elif isinstance(self.grid[i][j], StoreLowTier):
                    grid_str += " sl"
                elif isinstance(self.grid[i][j], StoreMidTier):
                    grid_str += " sm"
            grid_str += "\n"
        return grid_str

    def get_location(self,object) -> tuple: 
        from Household import Household
        if object == None:
            return None
        for x in range(len(self.grid)): 
            for y in range(len(self.grid[0])):
                if self.grid[x][y] == object:
                    return (x,y)
                
    def get_grid(self, gridsize:int): 
        sqrt_n = math.isqrt(gridsize)
        x_dim = sqrt_n
        
        while sqrt_n * x_dim < gridsize: 
            sqrt_n += 1 
            
        return [[None] * x_dim for _ in range(sqrt_n)]
    
    def assign_location(self, object): 
        index = random.randint(0, len(self.available_positions) - 1)
        row, col = self.available_positions.pop(index)
        self.grid[row][col] = object
        
    def get_travel_time_one_way(self,start:tuple,destination:tuple): 
        '''
        1x travel distance
        '''
        return math.sqrt(math.pow((start[0]- destination[0]),2) + math.pow((start[1]- destination[1]),2)) * self.time_per_cell
    
    def get_travel_time_entire_trip(self, start,stores):
        first_stop = self.get_location(stores[0])
        start = self.get_location(start)
        if len(stores) > 1:
            second_stop = self.get_location(stores[1])
            return self.get_travel_time_one_way(start, first_stop) + self.get_travel_time_one_way(first_stop, second_stop) + self.get_travel_time_one_way(second_stop, start) +\
            2 * globals.GRID_TIME_PER_STORE
        else:
            return self.get_travel_time_one_way(start, first_stop) * 2 + globals.GRID_TIME_PER_STORE
  
    def get_stores_within_time_constraint(self,start, avail_time:float, fg:str=None, needs_lower_tier:boolean=False, first_stop:Store=None): #assuming up to single travel 
        '''
        start and stops are stores/households
        
        if fg is missing -> add fg param
        if needs lowertier store -> needs_lower_tier = True, first_stop = entry
        
        not fg and lower_tier at the same time 
        
        '''
        #get relevant subgrid iterate through -> select stores
        #TODO check variations of method
        relevant_stores = []
      
        number_grids = int(avail_time/self.time_per_cell*2) #both ways included
        (x,y) = self.get_location(start)
        
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
            y_max = len(self.grid[0])-1
            
        first_location = None
        if first_stop != None:
            first_location = self.get_location(first_stop)
        if needs_lower_tier:
            tier = first_stop.store_type.tier
        for x_tmp in range(x_min,x_max):
            for y_tmp in range(y_min,y_max):
                if isinstance(self.grid[x_tmp][y_tmp], Store): 
                    stores = [self.grid[x_tmp][y_tmp]]
                    if first_location != None:
                        stores.append(first_location)
                    traveling_time= self.get_travel_time_entire_trip(start,stores) #we just go the other way round for easier calc
                    
                    if traveling_time <= avail_time:
                        if fg != None: #we need to find a store that offers a specifc fg
                            if self.grid[x_tmp][y_tmp].is_fg_in_productrange(fg):
                                relevant_stores.append(self.grid[x_tmp][y_tmp])
                        elif needs_lower_tier:
                            if self.grid[x_tmp][y_tmp].store_type.tier < tier:
                                relevant_stores.append(self.grid[x_tmp][y_tmp])
                        else:
                            relevant_stores.append(self.grid[x_tmp][y_tmp])
                    
        return relevant_stores
    