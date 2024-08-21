import globals
from Store import Store
from Grid import Grid
from EnumStoreTier import EnumStoreTier


class StoreConvenientStore(Store): 
    def __init__(self, store_type:EnumStoreTier, grid:Grid, id) -> None:
        super().__init__(store_type, grid,id)
        
        self.quality:float = globals.STORE_LOW_QUALITY  # type: ignore
        self.price:float = globals.STORE_LOW_PRICE # type: ignore #TODO calc based on stock avg p serving?
        # high price is expensive, low is cheap -> 1-price in formulas
        
        self.buy_stock(amount_per_item=100)
        