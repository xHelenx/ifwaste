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
        grid_str = ""
        for i in range(len(self.grid))   :
            for j in range(len(self.grid[0])):
                if self.grid[i][j] == None:
                    grid_str += " -"
                if isinstance(self.grid[i][j], Household):
                    grid_str += " h"
                elif isinstance(self.grid[i][j], Store):
                    grid_str += " s"
            grid_str += "\n"
        return grid_str
                
    
    def get_location(self,object) -> tuple: 
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
        return math.sqrt(math.pow((start[0]- destination[0]),2) + math.pow((start[1]- destination[1]),2)) * self.time_per_cell
        #TODO does not include time instore atm
    
    def get_travel_time_entire_route(nodes): 
        return NotImplementedError #best route between nodes
        #TODO 
        
    def get_relevant_stores(self,start, avail_time): #assuming up to single travel 
        #get relevant subgrid iterate through -> select stores
        relevant_stores = []
      
        number_grids = int(avail_time/self.time_per_cell*2) #both ways included
        (x,y) = start 
        
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
            
        for x_tmp in range(x_min,x_max):
            for y_tmp in range(y_min,y_max):
                if isinstance(self.grid[x_tmp][y_tmp], Store): 
                    print(start, (x_tmp, y_tmp))
                    if self.get_travel_time_one_way(start,(x_tmp,y_tmp)) * 2 <= avail_time:
                        relevant_stores.append(self.grid[x_tmp][y_tmp])
                
        return relevant_stores
        
        
    def get_relevant_store_types(avail_time):
        return NotImplementedError