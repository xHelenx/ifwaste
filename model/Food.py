import random
import globals 

class Food():
    def __init__(self, food_data:dict):
        """Creates a new food product based on the chosen food_data

        Args:
            food_data (dict): Food data includes type, expiration intervals, 
            servings, price, kg, kcal per kg, and amount of edible parts per kg
        """        
        self.type = food_data['type']
        self.servings = food_data['servings']
        self.days_till_expiry = food_data["days_till_expiry"]
        
    def __str__(self) -> str:
        """returns a readable string of a food

        Returns:
            str: includes expiration data, kcal and servings
        """        
        return "type: "  +  str(self.type) + " exp: " + str(self.days_till_expiry) +  " servings: " + str(self.servings) 
    
    def decay(self):
        """Decays food by reducing the expiration dates
        """        
        if not self.frozen:
            self.days_till_expiry -= 1
    
    #TODO redo
    def split(self, servings: int = None, kcal: float = None):
        """Splits the current meal into the portion as defined through the 
        amount of calories XOR the servings

        Args:
            kcal (float): required calories
            servings (float): required servings 

        return: [portioned_food(Food), leftover_food(Food)]  returns the meal into two portions, the first one being 
        the one as defined by kcal/servings and the second the leftover_food. May be empty
        """  
        if servings == None and kcal == None:
            raise ValueError('Must specify either servings or kcal')
        elif servings != None and kcal != None:
            raise ValueError('Must specify either servings or kcal, not both')
        elif servings != None: ##Serving based
            if servings > self.servings:
                servings = self.servings
            
            #calc how much of each servings is now in portioned food 
            scaler = servings/self.servings_per_type.values.sum()
            servings_per_type = self.servings_per_type.apply(lambda x: scaler * x).copy()
            portioned_food = Food({
                'Type': self.type,
                'kg': servings*self.serving_size,
                'Expiration Min.': self.exp,
                'Expiration Max.': self.exp,
                'Price': self.price_kg,
                'Servings': servings,
                'kcal_kg': self.kcal_kg,
                'Inedible Parts': self.inedible_parts,
                'ServingsPerType': servings_per_type,   
            })            
            
            self.kg -= portioned_food.kg
            self.price = self.kg * self.price_kg
            self.servings -= portioned_food.servings
            self.servings_per_type -= servings_per_type
            #assert self.servings_per_type.values.sum() == self.servings
            #assert portioned_food.servings_per_type.values.sum() == portioned_food.servings
            
        elif kcal != None: ##Kcal based
            if kcal > self.kcal_kg*self.kg:
                kcal = self.kcal_kg*self.kg
            servings = (kcal/self.kcal_kg)/self.serving_size
            servings_per_type = self.servings_per_type.apply(lambda x: (servings/self.servings_per_type.values.sum()) * x) 
            portioned_food = Food({
                'Type': self.type,
                'kg': kcal/self.kcal_kg,
                'Expiration Min.': self.exp,
                'Expiration Max.': self.exp,
                'Price': self.price_kg,
                'Servings': (kcal/self.kcal_kg)/self.serving_size,
                'kcal_kg': self.kcal_kg,
                'Inedible Parts': self.inedible_parts,
                'ServingsPerType': servings_per_type 
            })
            
            self.kg -= portioned_food.kg
            self.price = self.kg * self.price
            self.servings -= portioned_food.servings
            self.servings_per_type -= servings_per_type
                
        if self.servings_per_type.values.sum() < 0.01 : #todo might be removed when added plate waste
            #if self.servings_per_type.values.sum() > 0: 
                #print(self.servings_per_type.values.sum())
            self = None 
        
        #assert self == None or self.servings_per_type.values.sum() >=  0
        return (portioned_food, self)
    
    def split_waste_from_food(self, waste_type, plate_waste_ratio=None): 
        """Splits the current meal into waste and consumable food as defined through
        waste_type. 

            waste_type = [globals.FW_PLATE_WASTE, globals.FW_INEDIBLE, globals.FW_EXPIRED]
            plate_waste_ratio = if globals.FW_PLATE_WASTE is selected, define the plate_waste_ratio

        Args:
            kcal (float): required calories
            servings (float): required servings 

        return: [edible food (Food), waste(Food)]  returns the meal into two portions, the first one being 
        edible part and the second one the waste of the waste_type defined above. 
        """  
        assert waste_type != globals.FW_PLATE_WASTE or (waste_type == globals.FW_PLATE_WASTE and plate_waste_ratio != None)
        
        if waste_type == globals.FW_INEDIBLE:
            if self.inedible_parts > 0:
                waste_kg = self.kg * self.inedible_parts
                waste_servings = self.servings * self.inedible_parts
                waste_servings_per_type = self.servings_per_type.apply(lambda x: (waste_servings/self.servings_per_type.values.sum()) * x) 
                waste = Food({
                'Type': self.type,
                'kg': waste_kg,
                'Expiration Min.': self.exp,
                'Expiration Max.': self.exp,
                'Price': self.price_kg,
                'Servings': waste_servings,
                'kcal_kg': self.kcal_kg,
                'Inedible Parts': 1,
                'ServingsPerType': waste_servings_per_type 
                })
                self.inedible_parts = 0 #all inedible parts are now removed
            else: 
                return (self,None)
        elif waste_type == globals.FW_PLATE_WASTE: 
                waste_kg = self.kg * plate_waste_ratio
                waste_servings = self.servings * plate_waste_ratio
                waste_servings_per_type = self.servings_per_type.apply(lambda x: (waste_servings/self.servings_per_type.values.sum()) * x) 
                waste = Food({
                'Type': self.type,
                'kg': waste_kg,
                'Expiration Min.': self.exp,
                'Expiration Max.': self.exp,
                'Price': self.price_kg,
                'Servings': waste_servings,
                'kcal_kg': self.kcal_kg,
                'Inedible Parts': self.inedible_parts,
                'ServingsPerType': waste_servings_per_type 
                })
        else: 
            raise Exception("Used non existent waste_type in split()")
        
        
        waste.status = waste_type   
        self.kg -= waste.kg
        self.servings -= waste.servings
        self.servings_per_type -= waste_servings_per_type   
        return (self,waste)
            
    def get_kcal(self): 
        return self.kcal_kg * self.kg
    
    def __lt__(self, other):
        return self.exp < other.exp