from enum import Enum

class EnumStoreTier(Enum):
    CONVENIENCETIER = "Convenience_store", 0
    DISCOUNTRETAILER = "Discount_retailer", 1
    PREMIUMTIER = "Premium_retailer", 2
    

    def __new__(cls, name, tier):
        obj = object.__new__(cls)
        obj._name:str = name  # type: ignore # Store the name as _name
        obj._tier:int = tier  # type: ignore # Store the tier as _tier
        return obj

    @property
    def name(self) -> str:
        return self._name # type: ignore

    @property
    def tier(self) -> int:
        return self._tier # type: ignore
