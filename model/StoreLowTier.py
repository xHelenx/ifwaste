

import pandas as pd
import globals
import json

from FoodGroups import FoodGroups
from Store import Store
from Grid import Grid
from EnumStoreTier import EnumStoreTier


class StoreLowTier(Store):
    def __init__(self, store_type:EnumStoreTier, grid:Grid, id) -> None:
        super().__init__(store_type, grid,id)
        
        self.quality:float = 0.5 #todo
        self.price:float = 0.5 #TODO calc based on stock avg p serving?
        # high price is expensive, low is cheap -> 1-price in formulas
        
        self.buy_stock(amount_per_item=100)
        