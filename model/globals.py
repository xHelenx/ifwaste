import logging
import os
import random
import json

from EnumDiscountEffect import EnumDiscountEffect
from EnumSales import EnumSales

DAY = 0

SALES_TIMER_PLACEHOLDER = 1000

## Constants - DONT CHANGE
CONFIG_PATH = 'config.json'
### Food types
logger_hh = None 
logger_store = None 

FGMEAT = "FGMEAT"
FGDAIRY = "FGDAIRY"
FGVEGETABLE = "FGVEGETABLE"
FGDRYFOOD = "FGDRYFOOD"
FGBAKED = "FGBAKED"
FGSNACKS = "FGSNACKS"
FGSTOREPREPARED = "FGSTOREPREPARED"


STATUS_PREPARED = "Prepared"
STATUS_UNPREPARED = "Unprepared"
STATUS_PREPREPARED = "Preprepared"


### Waste types 
FW_PLATE_WASTE = "Plate Waste"
FW_INEDIBLE = "Inedible Parts"
FW_SPOILED = "Spoiled Food"

MALE = 0 
FEMALE = 1

##----------------------------------------------------
## General 
EXPIRATION_THRESHOLD = 4
MIN_TIME_TO_COOK = 0.8 #at least 30min to make a meal with 5 ingredients 
SERVINGS_PER_GRAB = 8
KCAL_PER_GRAB = 100 
INGREDIENTS_PER_QUICKCOOK = 3
MAX_SCALER_COOKING_AMOUNT = 2
##----------------------------------------------------
## Person 
ADULT_AGE_MIN = 18 
ADULT_AGE_MAX = 65 

#-----------------------------------------

HH_AMOUNT_CHILDREN = None
HH_AMOUNT_ADULTS = None
HH_OVER_BUDGET_FACTOR = None
HH_MAX_AVAIL_TIME_PER_DAY = None
HH_IMPULSE_BUY_PERCENTAGE = None

NEIGHBORHOOD_HOUSES = None
NEIGHBORHOOD_STORE_TYPES = None 
NEIGHBORHOOD_STORE_AMOUNTS = None 
NEIGHBORHOOD_PAY_DAY_INTERVAL = None

GRID_TRAVEL_TIME_PER_CELL = None 
GRID_TIME_PER_STORE = None

SIMULATION_RUNS = None
SIMULATION_DAYS = None
SIMULATION_OUTPUTFOLDER = None 
SIMULATION_WRITE_TO_FILE_INTERVAL = None
SIMULATION_DEBUG_LOG_ON = None

STORE_RESTOCK_INTERVAL = None 
STORE_BASELINE_STOCK = None

STORE_CON_QUALITY = None
STORE_CON_PRICE = None
STORE_CON_SAL_HIGH_STOCK_INTERVAL_1 = None
STORE_CON_SAL_HIGH_STOCK_INTERVAL_2 = None
STORE_CON_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_1 = None 
STORE_CON_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_2 = None 
STORE_CON_SAL_SEASONAL_LIKELIHOOD = None
STORE_CON_SAL_SEASONAL_DISCOUNT = None
STORE_CON_SAL_SEASONAL_DURATION = None
STORE_CON_SAL_CLEARANCE_INTERVAL_1 = None
STORE_CON_SAL_CLEARANCE_INTERVAL_2 = None
STORE_CON_SAL_CLEARANCE_INTERVAL_3 = None
STORE_CON_SAL_CLEARANCE_DISCOUNT_1 = None
STORE_CON_SAL_CLEARANCE_DISCOUNT_2 = None
STORE_CON_SAL_CLEARANCE_DISCOUNT_3  = None

STORE_DIS_QUALITY = None 
STORE_DIS_PRICE = None
STORE_DIS_SAL_HIGH_STOCK_INTERVAL_1 = None
STORE_DIS_SAL_HIGH_STOCK_INTERVAL_2 = None
STORE_DIS_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_1 = None 
STORE_DIS_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_2 = None 
STORE_DIS_SAL_SEASONAL_LIKELIHOOD = None
STORE_DIS_SAL_SEASONAL_DISCOUNT = None
STORE_DIS_SAL_SEASONAL_DURATION = None
STORE_DIS_SAL_CLEARANCE_INTERVAL_1 = None
STORE_DIS_SAL_CLEARANCE_INTERVAL_2 = None
STORE_DIS_SAL_CLEARANCE_INTERVAL_3 = None
STORE_DIS_SAL_CLEARANCE_DISCOUNT_1 = None
STORE_DIS_SAL_CLEARANCE_DISCOUNT_2 = None
STORE_DIS_SAL_CLEARANCE_DISCOUNT_3  = None

STORE_PRE_QUALITY = None
STORE_PRE_PRICE = None
STORE_PRE_SAL_HIGH_STOCK_INTERVAL_1 = None
STORE_PRE_SAL_HIGH_STOCK_INTERVAL_2 = None
STORE_PRE_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_1 = None
STORE_PRE_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_2 = None
STORE_PRE_SAL_SEASONAL_LIKELIHOOD = None
STORE_PRE_SAL_SEASONAL_DISCOUNT = None
STORE_PRE_SAL_SEASONAL_DURATION = None

STORE_PRE_SAL_CLEARANCE_INTERVAL_1 = None
STORE_PRE_SAL_CLEARANCE_INTERVAL_2 = None
STORE_PRE_SAL_CLEARANCE_INTERVAL_3 = None
STORE_PRE_SAL_CLEARANCE_DISCOUNT_1 = None
STORE_PRE_SAL_CLEARANCE_DISCOUNT_2 = None
STORE_PRE_SAL_CLEARANCE_DISCOUNT_3 = None

STORE_PREMIUM_QUALITY = None 
STORE_PREMIUM_PRICE = None

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
ADULT_MALE_MEAT_SERVINGS_MIN = None 
ADULT_MALE_MEAT_SERVINGS_MIN = None 
ADULT_MALE_SNACKS_SERVINGS_MIN = None 
ADULT_MALE_SNACKS_SERVINGS_MAX = None 
ADULT_MALE_BAKED_SERVINGS_MIN = None 
ADULT_MALE_BAKED_SERVINGS_MAX = None 
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
ADULT_FEMALE_MEAT_SERVINGS_MIN = None 
ADULT_FEMALE_MEAT_SERVINGS_MIN = None 
ADULT_FEMALE_SNACKS_SERVINGS_MIN = None 
ADULT_FEMALE_SNACKS_SERVINGS_MAX = None 
ADULT_FEMALE_BAKED_SERVINGS_MIN = None 
ADULT_FEMALE_BAKED_SERVINGS_MAX = None 
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
CHILD_MALE_MEAT_SERVINGS_MIN = None 
CHILD_MALE_MEAT_SERVINGS_MIN = None 
CHILD_MALE_SNACKS_SERVINGS_MIN = None 
CHILD_MALE_SNACKS_SERVINGS_MAX = None 
CHILD_MALE_BAKED_SERVINGS_MIN = None 
CHILD_MALE_BAKED_SERVINGS_MAX = None 
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
CHILD_FEMALE_MEAT_SERVINGS_MIN = None 
CHILD_FEMALE_MEAT_SERVINGS_MIN = None 
CHILD_FEMALE_SNACKS_SERVINGS_MIN = None 
CHILD_FEMALE_SNACKS_SERVINGS_MAX = None 
CHILD_FEMALE_BAKED_SERVINGS_MIN = None 
CHILD_FEMALE_BAKED_SERVINGS_MAX = None 
CHILD_FEMALE_STORE_PREPARED_SERVINGS_MIN = None 
CHILD_FEMALE_STORE_PREPARED_SERVINGS_MAX = None 

DEALASSESSOR_WEIGHT_SERVING_PRICE = None

BASKETCURATOR_INCREMENT_LIKELIHOOD = None 
BASKETCURATOR_MAX_ITEMS_QUICKSHOP = None

def to_EnumDiscountEffect(discount_effect: str) -> EnumDiscountEffect:
    if "." in discount_effect: 
        discount_effect = discount_effect.split('.')[-1]
    if discount_effect in EnumDiscountEffect.__members__:
        return EnumDiscountEffect[discount_effect]
    else:
        raise ValueError(f"{discount_effect} is not a valid EnumDiscountEffect")

def to_EnumSales(sale_type: str) -> EnumSales:
    if "." in sale_type: 
        sale_type = sale_type.split('.')[-1]
    if sale_type in EnumSales.__members__:
        return EnumSales[sale_type]
    raise ValueError(f"{sale_type} is not a valid EnumSales")

def configure_simulation(file) -> None: 
    global HH_AMOUNT_CHILDREN
    global HH_AMOUNT_ADULTS
    global HH_OVER_BUDGET_FACTOR
    global HH_MAX_AVAIL_TIME_PER_DAY
    global HH_IMPULSE_BUY_PERCENTAGE
    global NEIGHBORHOOD_HOUSES
    global NEIGHBORHOOD_STORE_TYPES
    global NEIGHBORHOOD_STORE_AMOUNTS    
    global GRID_TRAVEL_TIME_PER_CELL
    global GRID_TIME_PER_STORE
    global SIMULATION_RUNS
    global SIMULATION_DAYS
    global SIMULATION_OUTPUTFOLDER
    global SIMULATION_WRITE_TO_FILE_INTERVAL
    global SIMULATION_DEBUG_LOG_ON
    global EXPERIMENT_NAME
    
    global STORE_RESTOCK_INTERVAL
    global STORE_BASELINE_STOCK
    
    global STORE_CON_QUALITY
    global STORE_CON_PRICE
    global STORE_CON_SAL_HIGH_STOCK_INTERVAL_1
    global STORE_CON_SAL_HIGH_STOCK_INTERVAL_2
    global STORE_CON_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_2
    global STORE_CON_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_1 
    global STORE_CON_SAL_SEASONAL_LIKELIHOOD
    global STORE_CON_SAL_SEASONAL_DISCOUNT
    global STORE_CON_SAL_SEASONAL_DURATION
    global STORE_CON_SAL_CLEARANCE_INTERVAL_1
    global STORE_CON_SAL_CLEARANCE_INTERVAL_2
    global STORE_CON_SAL_CLEARANCE_INTERVAL_3
    global STORE_CON_SAL_CLEARANCE_DISCOUNT_1
    global STORE_CON_SAL_CLEARANCE_DISCOUNT_2
    global STORE_CON_SAL_CLEARANCE_DISCOUNT_3
    global STORE_DIS_QUALITY
    global STORE_DIS_PRICE
    global STORE_DIS_SAL_HIGH_STOCK_INTERVAL_1
    global STORE_DIS_SAL_HIGH_STOCK_INTERVAL_2
    global STORE_DIS_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_2
    global STORE_DIS_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_1 
    global STORE_DIS_SAL_SEASONAL_LIKELIHOOD
    global STORE_DIS_SAL_SEASONAL_DISCOUNT
    global STORE_DIS_SAL_SEASONAL_DURATION
    global STORE_DIS_SAL_CLEARANCE_INTERVAL_1
    global STORE_DIS_SAL_CLEARANCE_INTERVAL_2
    global STORE_DIS_SAL_CLEARANCE_INTERVAL_3
    global STORE_DIS_SAL_CLEARANCE_DISCOUNT_1
    global STORE_DIS_SAL_CLEARANCE_DISCOUNT_2
    global STORE_DIS_SAL_CLEARANCE_DISCOUNT_3
    global STORE_PRE_QUALITY
    global STORE_PRE_PRICE
    global STORE_PRE_SAL_HIGH_STOCK_INTERVAL_1
    global STORE_PRE_SAL_HIGH_STOCK_INTERVAL_2
    global STORE_PRE_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_1
    global STORE_PRE_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_2
    global STORE_PRE_SAL_SEASONAL_LIKELIHOOD
    global STORE_PRE_SAL_SEASONAL_DISCOUNT
    global STORE_PRE_SAL_SEASONAL_DURATION
    global STORE_PRE_SAL_CLEARANCE_INTERVAL_1
    global STORE_PRE_SAL_CLEARANCE_INTERVAL_2
    global STORE_PRE_SAL_CLEARANCE_INTERVAL_3
    global STORE_PRE_SAL_CLEARANCE_DISCOUNT_1
    global STORE_PRE_SAL_CLEARANCE_DISCOUNT_2
    global STORE_PRE_SAL_CLEARANCE_DISCOUNT_3   
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
    global ADULT_MALE_MEAT_SERVINGS_MIN
    global ADULT_MALE_MEAT_SERVINGS_MIN
    global ADULT_MALE_SNACKS_SERVINGS_MIN
    global ADULT_MALE_SNACKS_SERVINGS_MAX 
    global ADULT_MALE_BAKED_SERVINGS_MIN
    global ADULT_MALE_BAKED_SERVINGS_MAX
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
    global ADULT_FEMALE_MEAT_SERVINGS_MIN
    global ADULT_FEMALE_MEAT_SERVINGS_MIN
    global ADULT_FEMALE_SNACKS_SERVINGS_MIN
    global ADULT_FEMALE_SNACKS_SERVINGS_MAX
    global ADULT_FEMALE_BAKED_SERVINGS_MIN
    global ADULT_FEMALE_BAKED_SERVINGS_MAX
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
    global CHILD_MALE_MEAT_SERVINGS_MIN
    global CHILD_MALE_MEAT_SERVINGS_MIN
    global CHILD_MALE_SNACKS_SERVINGS_MIN
    global CHILD_MALE_SNACKS_SERVINGS_MAX
    global CHILD_MALE_BAKED_SERVINGS_MIN
    global CHILD_MALE_BAKED_SERVINGS_MAX
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
    global CHILD_FEMALE_MEAT_SERVINGS_MIN
    global CHILD_FEMALE_MEAT_SERVINGS_MIN
    global CHILD_FEMALE_SNACKS_SERVINGS_MIN
    global CHILD_FEMALE_SNACKS_SERVINGS_MAX
    global CHILD_FEMALE_BAKED_SERVINGS_MIN
    global CHILD_FEMALE_BAKED_SERVINGS_MAX
    global CHILD_FEMALE_STORE_PREPARED_SERVINGS_MIN
    global CHILD_FEMALE_STORE_PREPARED_SERVINGS_MAX
    global NEIGHBORHOOD_PAY_DAY_INTERVAL
    global DEALASSESSOR_WEIGHT_SERVING_PRICE
    global BASKETCURATOR_INCREMENT_LIKELIHOOD
    global BASKETCURATOR_MAX_ITEMS_QUICKSHOP
        
    print(file)
    print(os.getcwd())
    with open(file) as f:
        config = json.load(f)
            
    SIMULATION_RUNS = config["Simulation"]["runs"]
    SIMULATION_DAYS = config["Simulation"]["total_days"]
    SIMULATION_OUTPUTFOLDER = config["Simulation"]["output_folder"]
    SIMULATION_WRITE_TO_FILE_INTERVAL = config["Simulation"]["write_to_file_interval"]
    SIMULATION_DEBUG_LOG_ON = config["Simulation"]["debug_log_on"]
    EXPERIMENT_NAME = config["Simulation"]["name"]
    
    
    NEIGHBORHOOD_HOUSES = config["Neighborhood"]["neighborhood_houses"]
    
    store_types = config["Neighborhood"]["neighborhood_store_types"]
    parts = store_types.strip('[]').split(',')
    
    NEIGHBORHOOD_STORE_TYPES = [part.strip().strip("'") for part in parts]
    NEIGHBORHOOD_STORE_AMOUNTS = [int(item) for item in json.loads(config["Neighborhood"]["neighborhood_store_amounts"])]
    NEIGHBORHOOD_PAY_DAY_INTERVAL = config["Neighborhood"]["neighborhood_pay_day_interval"]
    
    GRID_TRAVEL_TIME_PER_CELL = config["Grid"]["travel_time_per_cell"]
    GRID_TIME_PER_STORE = config["Grid"]["tfloaime_per_store"]
    
    HH_AMOUNT_CHILDREN = config["Household"]["hh_amount_children"]
    HH_AMOUNT_ADULTS = config["Household"]["hh_amount_adults"]
    HH_OVER_BUDGET_FACTOR = config["Household"]["hh_over_budget_factor"]
    HH_MAX_AVAIL_TIME_PER_DAY = config["Household"]["hh_max_avail_time_per_day"]
    HH_IMPULSE_BUY_PERCENTAGE = config["Household"]["hh_impulse_buy_likelihood"]
    
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
    ADULT_MALE_MEAT_SERVINGS_MIN = config["Adult"]["male_meat_servings_min"]
    ADULT_MALE_MEAT_SERVINGS_MIN = config["Adult"]["male_meat_servings_min"]
    ADULT_MALE_SNACKS_SERVINGS_MIN = config["Adult"]["male_snacks_servings_min"]
    ADULT_MALE_SNACKS_SERVINGS_MAX = config["Adult"]["male_snacks_servings_max"]
    ADULT_MALE_BAKED_SERVINGS_MIN = config["Adult"]["male_baked_servings_min"]
    ADULT_MALE_BAKED_SERVINGS_MAX = config["Adult"]["male_baked_servings_max"]
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
    ADULT_FEMALE_MEAT_SERVINGS_MIN = config["Adult"]["female_meat_servings_min"]
    ADULT_FEMALE_MEAT_SERVINGS_MIN = config["Adult"]["female_meat_servings_min"]
    ADULT_FEMALE_SNACKS_SERVINGS_MIN = config["Adult"]["female_snacks_servings_min"]
    ADULT_FEMALE_SNACKS_SERVINGS_MAX = config["Adult"]["female_snacks_servings_max"]
    ADULT_FEMALE_BAKED_SERVINGS_MIN = config["Adult"]["female_baked_servings_min"]
    ADULT_FEMALE_BAKED_SERVINGS_MAX = config["Adult"]["female_baked_servings_max"]
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
    CHILD_MALE_MEAT_SERVINGS_MIN = config["Child"]["male_meat_servings_min"]
    CHILD_MALE_MEAT_SERVINGS_MIN = config["Child"]["male_meat_servings_min"]
    CHILD_MALE_SNACKS_SERVINGS_MIN = config["Child"]["male_snacks_servings_min"]
    CHILD_MALE_SNACKS_SERVINGS_MAX = config["Child"]["male_snacks_servings_max"]
    CHILD_MALE_BAKED_SERVINGS_MIN = config["Child"]["male_baked_servings_min"]
    CHILD_MALE_BAKED_SERVINGS_MAX = config["Child"]["male_baked_servings_max"]
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
    CHILD_FEMALE_MEAT_SERVINGS_MIN = config["Child"]["female_meat_servings_min"]
    CHILD_FEMALE_MEAT_SERVINGS_MIN = config["Child"]["female_meat_servings_min"]
    CHILD_FEMALE_SNACKS_SERVINGS_MIN = config["Child"]["female_snacks_servings_min"]
    CHILD_FEMALE_SNACKS_SERVINGS_MAX = config["Child"]["female_snacks_servings_max"]
    CHILD_FEMALE_BAKED_SERVINGS_MIN = config["Child"]["female_baked_servings_min"]
    CHILD_FEMALE_BAKED_SERVINGS_MAX = config["Child"]["female_baked_servings_max"]
    CHILD_FEMALE_STORE_PREPARED_SERVINGS_MIN = config["Child"]["female_store_prepared_servings_min"]
    CHILD_FEMALE_STORE_PREPARED_SERVINGS_MAX = config["Child"]["female_store_prepared_servings_max"]
    
    STORE_RESTOCK_INTERVAL = config["Store"]["restock_interval"]
    STORE_BASELINE_STOCK = config["Store"]["baseline_stock"]
    
    
    STORE_CON_QUALITY = config["Store"]["Convenience_store"]["quality"]
    STORE_CON_PRICE = config["Store"]["Convenience_store"]["price"]
    STORE_CON_SAL_HIGH_STOCK_INTERVAL_1 = config["Store"]["Convenience_store"]["Sales"]["high_stock_interval_1"]
    STORE_CON_SAL_HIGH_STOCK_INTERVAL_2 = config["Store"]["Convenience_store"]["Sales"]["high_stock_interval_2"]
    STORE_CON_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_1 = [to_EnumDiscountEffect(i) for i in config["Store"]["Convenience_store"]["Sales"]["high_stock_discount_interval_1"]]
    STORE_CON_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_2 = [to_EnumDiscountEffect(i) for i in config["Store"]["Convenience_store"]["Sales"]["high_stock_discount_interval_2"]]
    STORE_CON_SAL_SEASONAL_LIKELIHOOD = config["Store"]["Convenience_store"]["Sales"]["seasonal_likelihood"]
    STORE_CON_SAL_SEASONAL_DISCOUNT = [to_EnumDiscountEffect(i) for i in config["Store"]["Convenience_store"]["Sales"]["seasonal_discount"]]
    STORE_CON_SAL_SEASONAL_DURATION = config["Store"]["Convenience_store"]["Sales"]["seasonal_duration"]
    STORE_CON_SAL_CLEARANCE_INTERVAL_1 =  config["Store"]["Convenience_store"]["Sales"]["clearance_interval_1_expires_within"]
    STORE_CON_SAL_CLEARANCE_INTERVAL_2 = config["Store"]["Convenience_store"]["Sales"]["clearance_interval_2_expires_within"]
    STORE_CON_SAL_CLEARANCE_INTERVAL_3 = config["Store"]["Convenience_store"]["Sales"]["clearance_interval_3_expires_within"]
    STORE_CON_SAL_CLEARANCE_DISCOUNT_1 =  [to_EnumDiscountEffect(i) for i in config["Store"]["Convenience_store"]["Sales"]["clearance_interval_1_discount"]]
    STORE_CON_SAL_CLEARANCE_DISCOUNT_2 = [to_EnumDiscountEffect(i) for i in config["Store"]["Convenience_store"]["Sales"]["clearance_interval_2_discount"]]
    STORE_CON_SAL_CLEARANCE_DISCOUNT_3 = [to_EnumDiscountEffect(i) for i in config["Store"]["Convenience_store"]["Sales"]["clearance_interval_3_discount"]]
    
    STORE_DIS_QUALITY = config["Store"]["Discount_retailer"]["quality"]
    STORE_DIS_PRICE = config["Store"]["Discount_retailer"]["price"]
    STORE_DIS_SAL_HIGH_STOCK_INTERVAL_1 = config["Store"]["Discount_retailer"]["Sales"]["high_stock_interval_1"]
    STORE_DIS_SAL_HIGH_STOCK_INTERVAL_2 = config["Store"]["Discount_retailer"]["Sales"]["high_stock_interval_2"]
    STORE_DIS_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_1 = [to_EnumDiscountEffect(i) for i in config["Store"]["Discount_retailer"]["Sales"]["high_stock_discount_interval_1"]]
    STORE_DIS_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_2 = [to_EnumDiscountEffect(i) for i in config["Store"]["Discount_retailer"]["Sales"]["high_stock_discount_interval_2"]]
    STORE_DIS_SAL_SEASONAL_LIKELIHOOD = config["Store"]["Discount_retailer"]["Sales"]["seasonal_likelihood"]
    STORE_DIS_SAL_SEASONAL_DISCOUNT = [to_EnumDiscountEffect(i) for i in config["Store"]["Discount_retailer"]["Sales"]["seasonal_discount"]]
    STORE_DIS_SAL_SEASONAL_DURATION = config["Store"]["Discount_retailer"]["Sales"]["seasonal_duration"]
    STORE_DIS_SAL_CLEARANCE_INTERVAL_1 =  config["Store"]["Discount_retailer"]["Sales"]["clearance_interval_1_expires_within"]
    STORE_DIS_SAL_CLEARANCE_INTERVAL_2 = config["Store"]["Discount_retailer"]["Sales"]["clearance_interval_2_expires_within"]
    STORE_DIS_SAL_CLEARANCE_INTERVAL_3 = config["Store"]["Discount_retailer"]["Sales"]["clearance_interval_3_expires_within"]
    STORE_DIS_SAL_CLEARANCE_DISCOUNT_1 =  [to_EnumDiscountEffect(i) for i in config["Store"]["Discount_retailer"]["Sales"]["clearance_interval_1_discount"]]
    STORE_DIS_SAL_CLEARANCE_DISCOUNT_2 = [to_EnumDiscountEffect(i) for i in config["Store"]["Discount_retailer"]["Sales"]["clearance_interval_2_discount"]]
    STORE_DIS_SAL_CLEARANCE_DISCOUNT_3 = [to_EnumDiscountEffect(i) for i in config["Store"]["Discount_retailer"]["Sales"]["clearance_interval_3_discount"]]
    
    STORE_PRE_QUALITY = config["Store"]["Premium_retailer"]["quality"]
    STORE_PRE_PRICE = config["Store"]["Premium_retailer"]["price"]
    STORE_PRE_SAL_HIGH_STOCK_INTERVAL_1 = config["Store"]["Premium_retailer"]["Sales"]["high_stock_interval_1"]
    STORE_PRE_SAL_HIGH_STOCK_INTERVAL_2 = config["Store"]["Premium_retailer"]["Sales"]["high_stock_interval_2"]
    STORE_PRE_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_1 = [to_EnumDiscountEffect(i) for i in config["Store"]["Premium_retailer"]["Sales"]["high_stock_discount_interval_1"]]
    STORE_PRE_SAL_HIGH_STOCK_DISCOUNT_INTERVAL_2 = [to_EnumDiscountEffect(i) for i in config["Store"]["Premium_retailer"]["Sales"]["high_stock_discount_interval_2"]]
    STORE_PRE_SAL_SEASONAL_LIKELIHOOD = config["Store"]["Premium_retailer"]["Sales"]["seasonal_likelihood"]
    STORE_PRE_SAL_SEASONAL_DISCOUNT = [to_EnumDiscountEffect(i) for i in config["Store"]["Premium_retailer"]["Sales"]["seasonal_discount"]]
    STORE_PRE_SAL_SEASONAL_DURATION = config["Store"]["Premium_retailer"]["Sales"]["seasonal_duration"]
    STORE_PRE_SAL_CLEARANCE_INTERVAL_1 =  config["Store"]["Premium_retailer"]["Sales"]["clearance_interval_1_expires_within"]
    STORE_PRE_SAL_CLEARANCE_INTERVAL_2 = config["Store"]["Premium_retailer"]["Sales"]["clearance_interval_2_expires_within"]
    STORE_PRE_SAL_CLEARANCE_INTERVAL_3 = config["Store"]["Premium_retailer"]["Sales"]["clearance_interval_3_expires_within"]
    STORE_PRE_SAL_CLEARANCE_DISCOUNT_1 =  [to_EnumDiscountEffect(i) for i in config["Store"]["Premium_retailer"]["Sales"]["clearance_interval_1_discount"]]
    STORE_PRE_SAL_CLEARANCE_DISCOUNT_2 = [to_EnumDiscountEffect(i) for i in config["Store"]["Premium_retailer"]["Sales"]["clearance_interval_2_discount"]]
    STORE_PRE_SAL_CLEARANCE_DISCOUNT_3 = [to_EnumDiscountEffect(i) for i in config["Store"]["Premium_retailer"]["Sales"]["clearance_interval_3_discount"]]
    
    
    
    DEALASSESSOR_WEIGHT_SERVING_PRICE = config["DealAssessor"]["weight_serving_price"]
    
    BASKETCURATOR_INCREMENT_LIKELIHOOD = config["BasketCurator"]["increment_likelihood"]
    BASKETCURATOR_MAX_ITEMS_QUICKSHOP = config["BasketCurator"]["max_items_quickshop"]
    
def setup_logger() -> None:
    global logger_hh 
    global logger_store
    if SIMULATION_DEBUG_LOG_ON:
            
            logging.basicConfig(encoding="utf-8",level=logging.DEBUG, filemode="w")
            logger_hh = logging.getLogger("household")
            logger_store = logging.getLogger("store")
            handler_hh = logging.FileHandler('log_hh.log')
            handler_store = logging.FileHandler('log_store.log')

            logger_hh.addHandler(handler_hh)
            logger_store.addHandler(handler_store)