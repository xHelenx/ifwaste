from __future__ import annotations  # Delay import for type hints

class Location:
    def __init__(self,id:int, grid:Grid) -> None: # type: ignore
        self.id:int = id 
        self.grid: Grid  = grid # type: ignore
        
    def get_coordinates(self) -> tuple[int, int]: 
        return self.grid.get_coordinates(self)