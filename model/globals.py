import random
import json

## Constants - DONT CHANGE
### Food types
FTMEAT = "Meat & Fish" 
FTDAIRY = "Dairy & Eggs" 
FTVEGETABLE = "Fruits & Vegetables" 
FTDRYFOOD = "Dry Foods & Baked Goods" 
FTSNACKS = "Snacks, Condiments, Liquids, Oils, Grease, & Other" 
FTSTOREPREPARED ='Store-Prepared Items' 

### Waste types 
FW_PLATE_WASTE = "Plate Waste"
FW_INEDIBLE = "Inedible"
FW_EXPIRED = "Expired"

MALE = 0 
FEMALE = 1

##----------------------------------------------------
## General 
TOTAL_FOOD_TYPES = 6
EXPIRATION_THRESHOLD = 4
MIN_TIME_TO_COOK = 0.8 #at least 30min to make a meal with 5 ingredients 
MIN_TILL_SHOP = 5
SERVINGS_PER_GRAB = 8
INGREDIENTS_PER_QUICKCOOK = 2
SCALER_SHOPPING_AMOUNT = 5
##----------------------------------------------------
## Person 
ADULT_AGE_MIN = 18 
ADULT_AGE_MAX = 65 
ADULT_CONCERN_MIN = 0.3
ADULT_CONCERN_MAX = 0.7
## Child 
#CHILD_AGE = 
CHILD_CONCERN_MIN = 0
CHILD_CONCERN_MAX = 0.3

#-----------------------------------------
## Defined in config file: 
CHILD_PLATE_WASTE_MIN = None
CHILD_PLATE_WASTE_MAX = None

HH_AMOUNT_CHILDREN = None
HH_AMOUNT_ADULTS = None

ADULT_PLATE_WASTE_MIN = None
ADULT_PLATE_WASTE_MAX = None


NEIGHBORHOOD_HOUSES = None
NEIGHBORHOOD_SERVING_BASED = None

SIMULATION_RUNS = None
SIMULATION_DAYS = None

EXPERIMENT_NAME = None 
def configure_simulation(): 
    global CHILD_PLATE_WASTE_MIN
    global CHILD_PLATE_WASTE_MAX
    global HH_AMOUNT_CHILDREN
    global HH_AMOUNT_ADULTS
    global ADULT_PLATE_WASTE_MIN
    global ADULT_PLATE_WASTE_MAX
    global NEIGHBORHOOD_HOUSES
    global NEIGHBORHOOD_SERVING_BASED
    global SIMULATION_RUNS
    global SIMULATION_DAYS
    global EXPERIMENT_NAME
    with open('model/config.json') as f:
        config = json.load(f)

    CHILD_PLATE_WASTE_MIN = config["Child"]["child_plate_waste_min"]
    CHILD_PLATE_WASTE_MAX = config["Child"]["child_plate_waste_max"] 

    HH_AMOUNT_CHILDREN = config["House"]["hh_amount_children"]
    HH_AMOUNT_ADULTS = config["House"]["hh_amount_adults"]

    ADULT_PLATE_WASTE_MIN = config["Adult"]["adult_plate_waste_min"]
    ADULT_PLATE_WASTE_MAX = config["Adult"]["adult_plate_waste_max"] 


    NEIGHBORHOOD_HOUSES = config["Neighborhood"]["neighborhood_houses"]
    NEIGHBORHOOD_SERVING_BASED = config["Neighborhood"]["neighborhood_serving_based"]

            
    SIMULATION_RUNS = config["Simulation"]["runs"]
    SIMULATION_DAYS = config["Simulation"]["total_days"]
    EXPERIMENT_NAME = config["Simulation"]["name"]
        