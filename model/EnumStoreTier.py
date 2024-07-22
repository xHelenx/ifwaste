from enum import Enum

class EnumStoreTier(Enum):
    LOWTIER = "low-tier", 0
    MIDTIER = "mid-tier", 1
    HIGHTIER = "high-tier", 2

    def __new__(cls, name, tier):
        obj = object.__new__(cls)
        obj._name = name  # Store the name as _name
        obj._tier = tier  # Store the tier as _tier
        return obj

    @property
    def name(self):
        return self._name

    @property
    def tier(self):
        return self._tier
