import random
import json

## Constants - DONT CHANGE
CONFIG_PATH = 'model/config.json'
### Food types
FGMEAT = "FGMEAT"
FGDAIRY = "FGDAIRY"
FGVEGETABLE = "FGVEGETABLE"
FGDRYFOOD = "FGDRYFOOD"
FGSNACKS = "FGSNACKS"
FGSTOREPREPARED = "FGSTOREPREPARED"

### Waste types 
FW_PLATE_WASTE = "Plate Waste"
FW_INEDIBLE = "Inedible Parts"
FW_EXPIRED = "Spoiled Food"

MALE = 0 
FEMALE = 1

##----------------------------------------------------
## General 
TOTAL_FOOD_TYPES = 6
EXPIRATION_THRESHOLD = 4
MIN_TIME_TO_COOK = 0.8 #at least 30min to make a meal with 5 ingredients 
SERVINGS_PER_GRAB = 8
KCAL_PER_GRAB = 100 
INGREDIENTS_PER_QUICKCOOK = 2
MAX_SCALER_COOKING_AMOUNT = 2
SERVING_SIZES = [6,12,20]
##----------------------------------------------------
## Person 
ADULT_AGE_MIN = 18 
ADULT_AGE_MAX = 65 

#-----------------------------------------

HH_AMOUNT_CHILDREN = None
HH_AMOUNT_ADULTS = None


NEIGHBORHOOD_HOUSES = None
NEIGHBORHOOD_SERVING_BASED = None
NEIGHBORHOOD_STORE_TYPE = None 
NEIGHBORHOOD_STORE_AMOUNTS = None 
TRAVEL_TIME_PER_CELL = None 

SIMULATION_RUNS = None
SIMULATION_DAYS = None

EXPERIMENT_NAME = None 
ADULT_PLATE_WASTE_MIN = None 
ADULT_PLATE_WASTE_MAX = None 
ADULT_CONCERN_MIN = None 
ADULT_CONCERN_MAX = None 
ADULT_MALE_VEG_SERVINGS_MIN = None 
ADULT_MALE_VEG_SERVINGS_MAX = None 
ADULT_MALE_DRY_FOOD_SERVINGS_MIN = None 
ADULT_MALE_DRY_FOOD_SERVINGS_MAX = None 
ADULT_MALE_DAIRY_SERVINGS_MIN = None 
ADULT_MALE_DAIRY_SERVINGS_MAX = None 
ADULT_MALE_MEAT_SERVINGS_MIN = None 
ADULT_MALE_MEAT_SERVINGS_MAX = None 
ADULT_MALE_SNACKS_SERVINGS_MIN = None 
ADULT_MALE_SNACKS_SERVINGS_MAX = None 
ADULT_MALE_STORE_PREPARED_SERVINGS_MIN = None 
ADULT_MALE_STORE_PREPARED_SERVINGS_MAX = None 
ADULT_FEMALE_VEG_SERVINGS_MIN = None 
ADULT_FEMALE_VEG_SERVINGS_MAX = None 
ADULT_FEMALE_DRY_FOOD_SERVINGS_MIN = None 
ADULT_FEMALE_DRY_FOOD_SERVINGS_MAX = None 
ADULT_FEMALE_DAIRY_SERVINGS_MIN = None 
ADULT_FEMALE_DAIRY_SERVINGS_MAX = None 
ADULT_FEMALE_MEAT_SERVINGS_MIN = None 
ADULT_FEMALE_MEAT_SERVINGS_MAX = None 
ADULT_FEMALE_SNACKS_SERVINGS_MIN = None 
ADULT_FEMALE_SNACKS_SERVINGS_MAX = None 
ADULT_FEMALE_STORE_PREPARED_SERVINGS_MIN = None 
ADULT_FEMALE_STORE_PREPARED_SERVINGS_MAX = None 
CHILD_PLATE_WASTE_MIN = None 
CHILD_PLATE_WASTE_MAX = None 
CHILD_CONCERN_MIN = None 
CHILD_CONCERN_MAX = None 
CHILD_MALE_VEG_SERVINGS_MIN = None 
CHILD_MALE_VEG_SERVINGS_MAX = None 
CHILD_MALE_DRY_FOOD_SERVINGS_MIN = None 
CHILD_MALE_DRY_FOOD_SERVINGS_MAX = None 
CHILD_MALE_DAIRY_SERVINGS_MIN = None 
CHILD_MALE_DAIRY_SERVINGS_MAX = None 
CHILD_MALE_MEAT_SERVINGS_MIN = None 
CHILD_MALE_MEAT_SERVINGS_MAX = None 
CHILD_MALE_SNACKS_SERVINGS_MIN = None 
CHILD_MALE_SNACKS_SERVINGS_MAX = None 
CHILD_MALE_STORE_PREPARED_SERVINGS_MIN = None 
CHILD_MALE_STORE_PREPARED_SERVINGS_MAX = None 
CHILD_FEMALE_VEG_SERVINGS_MIN = None 
CHILD_FEMALE_VEG_SERVINGS_MAX = None 
CHILD_FEMALE_DRY_FOOD_SERVINGS_MIN = None 
CHILD_FEMALE_DRY_FOOD_SERVINGS_MAX = None 
CHILD_FEMALE_DAIRY_SERVINGS_MIN = None 
CHILD_FEMALE_DAIRY_SERVINGS_MAX = None 
CHILD_FEMALE_MEAT_SERVINGS_MIN = None 
CHILD_FEMALE_MEAT_SERVINGS_MAX = None 
CHILD_FEMALE_SNACKS_SERVINGS_MIN = None 
CHILD_FEMALE_SNACKS_SERVINGS_MAX = None 
CHILD_FEMALE_STORE_PREPARED_SERVINGS_MIN = None 
CHILD_FEMALE_STORE_PREPARED_SERVINGS_MAX = None 




def configure_simulation(): 
    global HH_AMOUNT_CHILDREN
    global HH_AMOUNT_ADULTS
    global NEIGHBORHOOD_HOUSES
    global NEIGHBORHOOD_SERVING_BASED
    global NEIGHBORHOOD_STORE_TYPE
    global NEIGHBORHOOD_STORE_AMOUNTS    
    global GRID_TRAVEL_TIME_PER_CELL
    global SIMULATION_RUNS
    global SIMULATION_DAYS
    global EXPERIMENT_NAME
    global ADULT_PLATE_WASTE_MIN
    global ADULT_PLATE_WASTE_MAX
    global ADULT_CONCERN_MIN
    global ADULT_CONCERN_MAX
    global ADULT_MALE_VEG_SERVINGS_MIN
    global ADULT_MALE_VEG_SERVINGS_MAX
    global ADULT_MALE_DRY_FOOD_SERVINGS_MIN
    global ADULT_MALE_DRY_FOOD_SERVINGS_MAX
    global ADULT_MALE_DAIRY_SERVINGS_MIN
    global ADULT_MALE_DAIRY_SERVINGS_MAX
    global ADULT_MALE_MEAT_SERVINGS_MIN
    global ADULT_MALE_MEAT_SERVINGS_MAX
    global ADULT_MALE_SNACKS_SERVINGS_MIN
    global ADULT_MALE_SNACKS_SERVINGS_MAX
    global ADULT_MALE_STORE_PREPARED_SERVINGS_MIN
    global ADULT_MALE_STORE_PREPARED_SERVINGS_MAX
    global ADULT_FEMALE_VEG_SERVINGS_MIN
    global ADULT_FEMALE_VEG_SERVINGS_MAX
    global ADULT_FEMALE_DRY_FOOD_SERVINGS_MIN
    global ADULT_FEMALE_DRY_FOOD_SERVINGS_MAX
    global ADULT_FEMALE_DAIRY_SERVINGS_MIN
    global ADULT_FEMALE_DAIRY_SERVINGS_MAX
    global ADULT_FEMALE_MEAT_SERVINGS_MIN
    global ADULT_FEMALE_MEAT_SERVINGS_MAX
    global ADULT_FEMALE_SNACKS_SERVINGS_MIN
    global ADULT_FEMALE_SNACKS_SERVINGS_MAX
    global ADULT_FEMALE_STORE_PREPARED_SERVINGS_MIN
    global ADULT_FEMALE_STORE_PREPARED_SERVINGS_MAX
    global CHILD_PLATE_WASTE_MIN
    global CHILD_PLATE_WASTE_MAX
    global CHILD_CONCERN_MIN
    global CHILD_CONCERN_MAX
    global CHILD_MALE_VEG_SERVINGS_MIN
    global CHILD_MALE_VEG_SERVINGS_MAX
    global CHILD_MALE_DRY_FOOD_SERVINGS_MIN
    global CHILD_MALE_DRY_FOOD_SERVINGS_MAX
    global CHILD_MALE_DAIRY_SERVINGS_MIN
    global CHILD_MALE_DAIRY_SERVINGS_MAX
    global CHILD_MALE_MEAT_SERVINGS_MIN
    global CHILD_MALE_MEAT_SERVINGS_MAX
    global CHILD_MALE_SNACKS_SERVINGS_MIN
    global CHILD_MALE_SNACKS_SERVINGS_MAX
    global CHILD_MALE_STORE_PREPARED_SERVINGS_MIN
    global CHILD_MALE_STORE_PREPARED_SERVINGS_MAX
    global CHILD_FEMALE_VEG_SERVINGS_MIN
    global CHILD_FEMALE_VEG_SERVINGS_MAX
    global CHILD_FEMALE_DRY_FOOD_SERVINGS_MIN
    global CHILD_FEMALE_DRY_FOOD_SERVINGS_MAX
    global CHILD_FEMALE_DAIRY_SERVINGS_MIN
    global CHILD_FEMALE_DAIRY_SERVINGS_MAX
    global CHILD_FEMALE_MEAT_SERVINGS_MIN
    global CHILD_FEMALE_MEAT_SERVINGS_MAX
    global CHILD_FEMALE_SNACKS_SERVINGS_MIN
    global CHILD_FEMALE_SNACKS_SERVINGS_MAX
    global CHILD_FEMALE_STORE_PREPARED_SERVINGS_MIN
    global CHILD_FEMALE_STORE_PREPARED_SERVINGS_MAX
   
    with open(CONFIG_PATH) as f:
        config = json.load(f)
            
    SIMULATION_RUNS = config["Simulation"]["runs"]
    SIMULATION_DAYS = config["Simulation"]["total_days"]
    EXPERIMENT_NAME = config["Simulation"]["name"]
        
    NEIGHBORHOOD_HOUSES = config["Neighborhood"]["neighborhood_houses"]
    NEIGHBORHOOD_SERVING_BASED = config["Neighborhood"]["neighborhood_serving_based"]
    NEIGHBORHOOD_STORE_TYPE = config["Neighborhood"]["neighborhood_store_types"]
    NEIGHBORHOOD_STORE_AMOUNTS = config["Neighborhood"]["neighborhood_store_amounts"]
    
    GRID_TRAVEL_TIME_PER_CELL = config["Grid"]["travel_time_per_cell"]
    
    HH_AMOUNT_CHILDREN = config["Household"]["hh_amount_children"]
    HH_AMOUNT_ADULTS = config["Household"]["hh_amount_adults"]
    
    #TRAVEL_TIME_PER_CELL = config["Grid"]["travel_time_per_cell"]
    
    ADULT_PLATE_WASTE_MIN = config["Adult"]["adult_plate_waste_min"]
    ADULT_PLATE_WASTE_MAX = config["Adult"]["adult_plate_waste_max"]
    ADULT_CONCERN_MIN = config["Adult"]["adult_concern_min"]
    ADULT_CONCERN_MAX = config["Adult"]["adult_concern_max"]
    ADULT_MALE_VEG_SERVINGS_MIN = config["Adult"]["male_veg_servings_min"]
    ADULT_MALE_VEG_SERVINGS_MAX = config["Adult"]["male_veg_servings_max"]
    ADULT_MALE_DRY_FOOD_SERVINGS_MIN = config["Adult"]["male_dry_food_servings_min"]
    ADULT_MALE_DRY_FOOD_SERVINGS_MAX = config["Adult"]["male_dry_food_servings_max"]
    ADULT_MALE_DAIRY_SERVINGS_MIN = config["Adult"]["male_dairy_servings_min"]
    ADULT_MALE_DAIRY_SERVINGS_MAX = config["Adult"]["male_dairy_servings_max"]
    ADULT_MALE_MEAT_SERVINGS_MIN = config["Adult"]["male_meat_servings_min"]
    ADULT_MALE_MEAT_SERVINGS_MAX = config["Adult"]["male_meat_servings_max"]
    ADULT_MALE_SNACKS_SERVINGS_MIN = config["Adult"]["male_snacks_servings_min"]
    ADULT_MALE_SNACKS_SERVINGS_MAX = config["Adult"]["male_snacks_servings_max"]
    ADULT_MALE_STORE_PREPARED_SERVINGS_MIN = config["Adult"]["male_store_prepared_servings_min"]
    ADULT_MALE_STORE_PREPARED_SERVINGS_MAX = config["Adult"]["male_store_prepared_servings_max"]
    ADULT_FEMALE_VEG_SERVINGS_MIN = config["Adult"]["female_veg_servings_min"]
    ADULT_FEMALE_VEG_SERVINGS_MAX = config["Adult"]["female_veg_servings_max"]
    ADULT_FEMALE_DRY_FOOD_SERVINGS_MIN = config["Adult"]["female_dry_food_servings_min"]
    ADULT_FEMALE_DRY_FOOD_SERVINGS_MAX = config["Adult"]["female_dry_food_servings_max"]
    ADULT_FEMALE_DAIRY_SERVINGS_MIN = config["Adult"]["female_dairy_servings_min"]
    ADULT_FEMALE_DAIRY_SERVINGS_MAX = config["Adult"]["female_dairy_servings_max"]
    ADULT_FEMALE_MEAT_SERVINGS_MIN = config["Adult"]["female_meat_servings_min"]
    ADULT_FEMALE_MEAT_SERVINGS_MAX = config["Adult"]["female_meat_servings_max"]
    ADULT_FEMALE_SNACKS_SERVINGS_MIN = config["Adult"]["female_snacks_servings_min"]
    ADULT_FEMALE_SNACKS_SERVINGS_MAX = config["Adult"]["female_snacks_servings_max"]
    ADULT_FEMALE_STORE_PREPARED_SERVINGS_MIN = config["Adult"]["female_store_prepared_servings_min"]
    ADULT_FEMALE_STORE_PREPARED_SERVINGS_MAX = config["Adult"]["female_store_prepared_servings_max"]
    CHILD_PLATE_WASTE_MIN = config["Child"]["child_plate_waste_min"]
    CHILD_PLATE_WASTE_MAX = config["Child"]["child_plate_waste_max"]
    CHILD_CONCERN_MIN = config["Child"]["child_concern_min"]
    CHILD_CONCERN_MAX = config["Child"]["child_concern_max"]
    CHILD_MALE_VEG_SERVINGS_MIN = config["Child"]["male_veg_servings_min"]
    CHILD_MALE_VEG_SERVINGS_MAX = config["Child"]["male_veg_servings_max"]
    CHILD_MALE_DRY_FOOD_SERVINGS_MIN = config["Child"]["male_dry_food_servings_min"]
    CHILD_MALE_DRY_FOOD_SERVINGS_MAX = config["Child"]["male_dry_food_servings_max"]
    CHILD_MALE_DAIRY_SERVINGS_MIN = config["Child"]["male_dairy_servings_min"]
    CHILD_MALE_DAIRY_SERVINGS_MAX = config["Child"]["male_dairy_servings_max"]
    CHILD_MALE_MEAT_SERVINGS_MIN = config["Child"]["male_meat_servings_min"]
    CHILD_MALE_MEAT_SERVINGS_MAX = config["Child"]["male_meat_servings_max"]
    CHILD_MALE_SNACKS_SERVINGS_MIN = config["Child"]["male_snacks_servings_min"]
    CHILD_MALE_SNACKS_SERVINGS_MAX = config["Child"]["male_snacks_servings_max"]
    CHILD_MALE_STORE_PREPARED_SERVINGS_MIN = config["Child"]["male_store_prepared_servings_min"]
    CHILD_MALE_STORE_PREPARED_SERVINGS_MAX = config["Child"]["male_store_prepared_servings_max"]
    CHILD_FEMALE_VEG_SERVINGS_MIN = config["Child"]["female_veg_servings_min"]
    CHILD_FEMALE_VEG_SERVINGS_MAX = config["Child"]["female_veg_servings_max"]
    CHILD_FEMALE_DRY_FOOD_SERVINGS_MIN = config["Child"]["female_dry_food_servings_min"]
    CHILD_FEMALE_DRY_FOOD_SERVINGS_MAX = config["Child"]["female_dry_food_servings_max"]
    CHILD_FEMALE_DAIRY_SERVINGS_MIN = config["Child"]["female_dairy_servings_min"]
    CHILD_FEMALE_DAIRY_SERVINGS_MAX = config["Child"]["female_dairy_servings_max"]
    CHILD_FEMALE_MEAT_SERVINGS_MIN = config["Child"]["female_meat_servings_min"]
    CHILD_FEMALE_MEAT_SERVINGS_MAX = config["Child"]["female_meat_servings_max"]
    CHILD_FEMALE_SNACKS_SERVINGS_MIN = config["Child"]["female_snacks_servings_min"]
    CHILD_FEMALE_SNACKS_SERVINGS_MAX = config["Child"]["female_snacks_servings_max"]
    CHILD_FEMALE_STORE_PREPARED_SERVINGS_MIN = config["Child"]["female_store_prepared_servings_min"]
    CHILD_FEMALE_STORE_PREPARED_SERVINGS_MAX = config["Child"]["female_store_prepared_servings_max"]