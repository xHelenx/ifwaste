import math
import random 


class Grid: 
    def __init__(self) -> None:
        gridsize = globals.NEIGHBORHOOD_HOUSES + sum(globals.NEIGHBORHOOD_StORE_AMOUNTS)
        #create grid that is as "square shaped as possible"      
        
        self.grid = self.get_grid(gridsize)    
        
        
    def get_grid(self, gridsize): 
        sqrt_n = math.isqrt(n)
        x_dim = sqrt_n
        
        while sqrt_n * x_dim < gridsize: 
            sqrt_n += 1 
            
        return [[None] * x_dim for _ in range(sqrt_n)]
    
    def assign_location(self, available_positions): 
        index = random.randint(0, len(available_positions) - 1)
        row, col = available_positions.pop(index)
        return (row,col)
        
    def get_travel_time_one_way(start:tuple,destination:tuple): 
        return math.sqrt(math.pow((start[0]- destination[0]),2) + math.pow((start[1]- destination[1]),2)) * globals.TRAVEL_TIME_PER_CELL
                         
    
    def get_travel_time_entire_route(nodes): 
        return NotImplementedError #best route between nodes
        #TODO 