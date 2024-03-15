import random
from Person import Person


class Child(Person):
    def __init__(self):
        super().__init__()
        self.age = random.randint(1, 18)
        self.kcal = random.gauss(1200, 200) + self.age*50
        