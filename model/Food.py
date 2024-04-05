import random


class Food():
    def __init__(self, food_data:dict):
        """Creates a new food product based on the chosen food_data

        Args:
            food_data (dict): Food data includes type, expiration intervals, 
            servings, price, kg, kcal per kg, and amount of edible parts per kg
        """        
        self.type = food_data['Type']
        self.kg = food_data['kg']
        self.servings = food_data['Servings']
        self.exp = random.randint(food_data['Expiration Min.'], food_data['Expiration Max.'])
        self.price_kg = food_data['Price']/self.kg
        self.inedible_parts = food_data['Inedible Parts']
        self.servings_per_type = food_data["ServingsPerType"].copy()
        self.frozen = False
        self.serving_size = self.kg/self.servings
        self.kcal_kg = food_data['kcal_kg']
        self.status = 'Un-prepped' if self.type != 'Store-Prepared Items' else 'Store-prepped'
    def __str__(self) -> str:
        """returns a readable string of a food

        Returns:
            str: includes expiration data, kcal and servings
        """        
        return "exp: " + str(self.exp) + " kcal: " + str(int(self.kcal_kg*self.kg)) + " servings: " + str(self.servings) + "type: "  + \
        str(self.servings_per_type.values)
    def decay(self):
        """Decays food by reducing the expiration dates
        """        
        if not self.frozen:
            self.exp -= 1
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
                'Price': self.price_kg*servings*self.serving_size,
                'Servings': servings,
                'kcal_kg': self.kcal_kg,
                'Inedible Parts': self.inedible_parts,
                'ServingsPerType': servings_per_type
            })
            self.kg -= portioned_food.kg
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
                'Price': self.price_kg*kcal/self.kcal_kg,
                'Servings': (kcal/self.kcal_kg)/self.serving_size,
                'kcal_kg': self.kcal_kg,
                'Inedible Parts': self.inedible_parts,
                'ServingsPerType': servings_per_type 
            })
            self.kg -= portioned_food.kg
            self.servings -= portioned_food.servings
            self.servings_per_type -= servings_per_type
                
        if self.kg <= 0.001 or self.servings <= 0.001:
            self = None 

        #assert self == None or self.servings_per_type.values.sum() >=  0
        return (portioned_food, self)
    
    def get_kcal(self): 
        return self.kcal_kg * self.kg
    
    def __lt__(self, other):
        return self.exp < other.exp