import random
from Person import Person


class Child(Person):
    def __init__(self, amount_children):
        """Initializes a child by:
        - age 
        - gender
        - kcal = kcal required per day
        - susceptibility = susceptibility to other opinions about economical, environmental and health concern
        within the household
        - concern = list of concern [env,eco,health], value between 0-1, 1 indicating a high concern

        """ 
        super().__init__()
        self.age = random.randint(1, 18)
        self.kcal = random.gauss(1200, 200) + self.age*50
        self.is_adult = False 
        self.susceptibility = 0
        self.concern = [random.uniform(0,0.3),random.uniform(0,0.3),random.uniform(0,0.3)]