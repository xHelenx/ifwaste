from Food import Food


class Inedible():
    def __init__(self, food:Food):
        # creates a waste from the inedible parts of a food
        self.type = food.type
        self.kg = food.kg*food.inedible_parts
        self.servings = food.servings
        self.price_kg = food.price_kg
        self.kcal_kg = 0
        self.status = 'Inedible'
        self.exp = None
        # update the food
        food.kg -= self.kg
        food.serving_size *= (1-food.inedible_parts)
        food.kcal_kg /= (1-food.inedible_parts) # assume inedible parts have no calories