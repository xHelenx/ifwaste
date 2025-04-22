
import globals
from Store import Store
from Grid import Grid
from EnumStoreTier import EnumStoreTier
from EnumDiscountEffect import EnumDiscountEffect


class StorePremimumRetailer(Store):
    def __init__(self, grid:Grid, id:int) -> None:
        """Initializes premimum retailer store. Here all information regarding the sales are set

        Args:
            store_type (EnumStoreTier): type of store
            grid (Grid): grid of the neighborhood
            id (int): store id 
        """        
        self.path_to_product_range = globals.STORE_PRE_PATH
        super().__init__(EnumStoreTier.PREMIUMTIER, grid, id)
        self.quality:float = globals.STORE_PRE_QUALITY # type: ignore # price is expensive, low is cheap -> 1-price in formulas
        
        
        self.high_stock_interval_1:float|None = globals.STORE_PRE_SAL_HIGH_STOCK_INTERVAL_1
        self.high_stock_interval_2:float|None = globals.STORE_PRE_SAL_HIGH_STOCK_INTERVAL_2
        self.high_stock_discount_1:list[EnumDiscountEffect] = globals.STORE_PRE_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_1
        self.high_stock_discount_2:list[EnumDiscountEffect] = globals.STORE_PRE_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_2
        self.seasonal_likelihood:float|None = globals.STORE_PRE_SAL_SEASONAL_LIKELIHOOD
        self.seasonal_discount:list[EnumDiscountEffect] = globals.STORE_PRE_SAL_SEASONAL_DISCOUNT
        self.seasonal_duration:float|None = globals.STORE_PRE_SAL_SEASONAL_DURATION
        self.clearance_interval_1:float|None = globals.STORE_PRE_SAL_CLEARANCE_INTERVAL_1
        self.clearance_interval_2:float|None = globals.STORE_PRE_SAL_CLEARANCE_INTERVAL_2
        self.clearance_interval_3:float|None = globals.STORE_PRE_SAL_CLEARANCE_INTERVAL_3
        self.clearance_discount_1:list[EnumDiscountEffect] = globals.STORE_PRE_SAL_CLEARANCE_DISCOUNT_1
        self.clearance_discount_2:list[EnumDiscountEffect] = globals.STORE_PRE_SAL_CLEARANCE_DISCOUNT_2
        self.clearance_discount_3:list[EnumDiscountEffect] = globals.STORE_PRE_SAL_CLEARANCE_DISCOUNT_3
        
        