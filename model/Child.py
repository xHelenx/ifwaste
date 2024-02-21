import random
from Person import Person


class Child(Person):
    def __init__(self, parent: Person):
        self.age = random.randint(1, 18)
        self.kcal = random.gauss(1200, 200) + self.age*50
        self.gender = random.randint(0,1) #1 is female
        self.parent = parent
