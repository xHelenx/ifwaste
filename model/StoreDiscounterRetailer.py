import globals_config as globals_config
from Store import Store
from Grid import Grid
from EnumStoreTier import EnumStoreTier
from EnumDiscountEffect import EnumDiscountEffect

class StoreDiscounterRetailer(Store):
    def __init__(self, grid:Grid, id:int) -> None:
        """Initializes premimum retailer store. Here all information regarding the sales are set

        Args:
            store_type (EnumStoreTier): type of store
            grid (Grid): grid of the neighborhood
            id (int): store id 
        """   
        self.path_to_product_range = globals_config.STORE_DIS_PATH[0]
        super().__init__(EnumStoreTier.DISCOUNTRETAILER, grid,id)
        self.quality:float = globals_config.STORE_DIS_QUALITY[0]  # type: ignore[0]
        self.high_stock_interval_1:float|None = globals_config.STORE_DIS_SAL_HIGH_STOCK_INTERVAL_1[0]
        self.high_stock_interval_2:float|None = globals_config.STORE_DIS_SAL_HIGH_STOCK_INTERVAL_2[0]
        self.high_stock_discount_1:list[EnumDiscountEffect] = globals_config.STORE_DIS_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_1[0]
        self.high_stock_discount_2:list[EnumDiscountEffect] = globals_config.STORE_DIS_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_2[0]
        self.seasonal_likelihood:float|None = globals_config.STORE_DIS_SAL_SEASONAL_LIKELIHOOD[0]
        self.seasonal_discount:list[EnumDiscountEffect] = globals_config.STORE_DIS_SAL_SEASONAL_DISCOUNT[0]
        self.seasonal_duration:float|None = globals_config.STORE_DIS_SAL_SEASONAL_DURATION[0]
        self.clearance_interval_1:float|None = globals_config.STORE_DIS_SAL_CLEARANCE_INTERVAL_1[0]
        self.clearance_interval_2:float|None = globals_config.STORE_DIS_SAL_CLEARANCE_INTERVAL_2[0]
        self.clearance_interval_3:float|None = globals_config.STORE_DIS_SAL_CLEARANCE_INTERVAL_3[0]
        self.clearance_discount_1:list[EnumDiscountEffect] = globals_config.STORE_DIS_SAL_CLEARANCE_DISCOUNT_1[0]
        self.clearance_discount_2:list[EnumDiscountEffect] = globals_config.STORE_DIS_SAL_CLEARANCE_DISCOUNT_2[0]
        self.clearance_discount_3:list[EnumDiscountEffect] = globals_config.STORE_DIS_SAL_CLEARANCE_DISCOUNT_3[0]
        