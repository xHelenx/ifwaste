import random


class Food():
    def __init__(self, food_data:dict):
        self.type = food_data['Type']
        self.kg = food_data['kg']
        self.servings = food_data['Servings']
        self.exp = random.randint(food_data['Expiration Min.'], food_data['Expiration Max.'])
        self.price_kg = food_data['Price']/self.kg
        self.inedible_parts = food_data['Inedible Parts']
        self.frozen = False
        self.serving_size = self.kg/self.servings
        self.kcal_kg = food_data['kcal_kg']
        self.status = 'Un-prepped' if self.type != 'Store-Prepared Items' else 'Store-prepped'
    def __str__(self) -> str:
        return "exp: " + str(self.exp) + " kcal: " + str(int(self.kcal_kg/self.kg)) + " servings: " + str(self.servings)
    def decay(self):
        if self.frozen == False:
            self.exp -= 1
    def split(self, f_list: list, 
        to_list: list = None, 
        servings: int = None, 
        kcal: float = None):
        to_list = f_list if to_list == None else to_list
        if servings == None and kcal == None:
            raise ValueError('Must specify either servings or kcal')
        elif servings != None and kcal != None:
            raise ValueError('Must specify either servings or kcal, not both')
        elif servings != None:
            if servings > self.servings:
                servings = self.servings
            new_food = Food({
                'Type': self.type,
                'kg': servings*self.serving_size,
                'Expiration Min.': self.exp,
                'Expiration Max.': self.exp,
                'Price': self.price_kg*servings*self.serving_size,
                'Servings': servings,
                'kcal_kg': self.kcal_kg,
                'Inedible Parts': self.inedible_parts
            })
            self.kg -= new_food.kg
            self.servings -= new_food.servings
            to_list.append(new_food)
        elif kcal != None:
            if kcal > self.kcal_kg*self.kg:
                kcal = self.kcal_kg*self.kg
            new_food = Food({
                'Type': self.type,
                'kg': kcal/self.kcal_kg,
                'Expiration Min.': self.exp,
                'Expiration Max.': self.exp,
                'Price': self.price_kg*kcal/self.kcal_kg,
                'Servings': (kcal/self.kcal_kg)/self.serving_size,
                'kcal_kg': self.kcal_kg,
                'Inedible Parts': self.inedible_parts
            })
            self.kg -= new_food.kg
            self.servings -= new_food.servings
            to_list.append(new_food)
        if self.kg <= 0.001 or self.servings <= 0.001:
            f_list.remove(self)
    def throw(self):
        # return a list of wasted food
        return [self]