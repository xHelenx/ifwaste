

import pandas as pd
import globals
import json

from FoodGroups import FoodGroups
from Store import Store
from Grid import Grid


class StoreLowTier(Store):
    def __init__(self, store_type:str, grid:Grid) -> None:
        super().__init__(store_type, grid)
        
        self.quality = 0.5 #todo
        self.price = 0.5 #TODO calc based on stock avg p serving?
        
        self.buy_stock(10)
        