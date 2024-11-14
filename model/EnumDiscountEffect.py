from enum import Enum


class EnumDiscountEffect(Enum): 
    NONE = "normal price",1
    DISCOUNT10 = "10% Discount",0.9
    DISCOUNT20 = "20% Discount",0.8
    DISCOUNT30 = "30% Discount",0.7
    DISCOUNT40 = "40% Discount",0.6
    DISCOUNT50 = "50% Discount",0.5
    DISCOUNT60 = "60% Discount",0.4
    BOGO = "BOGO", 2
    

    def __new__(cls, name, scaler):
        obj = object.__new__(cls)
        obj._name:str = name  # type: ignore # Store the name as _name
        obj._scaler:int = scaler  # type: ignore # Store the tier as _tier
        return obj

    @property
    def name(self) -> str:
        return self._name # type: ignore

    @property
    def scaler(self) -> int:
        return self._scaler # type: ignore
