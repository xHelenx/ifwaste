from enum import Enum


class EnumSales(Enum): 
    NONE = "normal price"
    SEASONAL = "seasonal sale"
    EXPIRING = "expiring soon"
    HIGHSTOCK = "high stock"
    
#class SalesType(Enum): 
#    BOGO = "BOGO"
#    SALES = "SALES"