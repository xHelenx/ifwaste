import random


class Person():
    def __init__(self, amount_adults=-1):
        """Initializes an adult person by:
        - age 
        - gender
        - kcal = kcal required per day
        - susceptibility = susceptibility to other opinions about economical, environmental and health concern
        within the household
        - concern = list of concern [env,eco,health], value between 0-1, 1 indicating a high concern

        """        
        self.age = random.randint(18, 65)
        self.gender = random.randint(0, 1) #1 is female
        self.kcal = random.gauss(2000, 500) - 500*self.gender
        self.is_adult = True
        self.susceptibility = 0
        self.concern = [random.uniform(0.3,0.7),random.uniform(0.3,0.7),random.uniform(0.3,0.7)]
    #def old(self):
    #    self.age += 1
    #    if self.age <= 18:
    #        self.kcal += 50 + 10*self.gender
    #    elif self.age > 30 and self.age <= 40:
    #        self.kcal -= 50 + 10*self.gender
