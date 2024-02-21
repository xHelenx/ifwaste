import random


class Person():
    def __init__(self):
        self.age = random.randint(18, 65)
        self.gender = random.randint(0, 1) #1 is female
        self.kcal = random.gauss(2000, 500) - 500*self.gender
    def old(self):
        self.age += 1
        if self.age <= 18:
            self.kcal += 50 + 10*self.gender
        elif self.age > 30 and self.age <= 40:
            self.kcal -= 50 + 10*self.gender
