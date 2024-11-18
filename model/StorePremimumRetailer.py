

import pandas as pd
import globals
import json

from FoodGroups import FoodGroups
from Store import Store
from Grid import Grid
from EnumStoreTier import EnumStoreTier
from EnumDiscountEffect import EnumDiscountEffect


class StorePremimumRetailer(Store):
    def __init__(self, store_type:EnumStoreTier, grid:Grid, id) -> None:
        super().__init__(store_type, grid, id)
        
        self.quality:float = globals.STORE_PREMIUM_QUALITY # type: ignore
        self.price:float = globals.STORE_PREMIUM_PRICE # type: ignore 
        # high 
        # price is expensive, low is cheap -> 1-price in formulas
        self.high_stock_interval_1:float|None = globals.STORE_PRE_SAL_HIGH_STOCK_INTERVAL_1
        self.high_stock_interval_2:float|None = globals.STORE_PRE_SAL_HIGH_STOCK_INTERVAL_2
        self.high_stock_discount_1:list[EnumDiscountEffect] = globals.STORE_PRE_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_1
        self.high_stock_discount_2:list[EnumDiscountEffect] = globals.STORE_PRE_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_1
        self.seasonal_likelihood:float|None = globals.STORE_PRE_SAL_SEASONAL_LIKELIHOOD
        self.seasonal_discount:list[EnumDiscountEffect] = globals.STORE_PRE_SAL_SEASONAL_DISCOUNT
        self.seasonal_duration:float|None = globals.STORE_PRE_SAL_SEASONAL_DURATION
        self.clearance_interval_1:float|None = globals.STORE_PRE_SAL_CLEARANCE_INTERVAL_1
        self.clearance_interval_2:float|None = globals.STORE_PRE_SAL_CLEARANCE_INTERVAL_2
        self.clearance_interval_3:float|None = globals.STORE_PRE_SAL_CLEARANCE_INTERVAL_3
        self.clearance_discount_1:list[EnumDiscountEffect] = globals.STORE_PRE_SAL_CLEARANCE_DISCOUNT_1
        self.clearance_discount_2:list[EnumDiscountEffect] = globals.STORE_PRE_SAL_CLEARANCE_DISCOUNT_2
        self.clearance_discount_3:list[EnumDiscountEffect] = globals.STORE_PRE_SAL_CLEARANCE_DISCOUNT_3
        
        