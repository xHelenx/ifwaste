import logging
import os
import json

from EnumDiscountEffect import EnumDiscountEffect
from EnumSales import EnumSales

DAY = 0

SALES_TIMER_PLACEHOLDER = 1000

## Constants - DONT CHANGE
CONFIG_PATH = '/blue/carpena/haasehelen/ifwaste/bash-scripts/experiments/config_trial.json'
### Food types
logger_hh = None 
logger_store = None 

LOG_TYPE_ACTIVE_DAY_SEPARATOR =True
LOG_TYPE_ACTIVE_TOTAL_SERV = True #TODO move to config
LOG_TYPE_ACTIVE_BASKET_ADJUSTMENT = False
LOG_TYPE_ACTIVE_STORE_TYPE = False
LOG_TYPE_ACTIVE_BASKET_COMPOSITION = False

LOG_TYPE_DAY_SEPARATOR = "day_separator"
LOG_TYPE_TOTAL_SERV = "total_serv"
LOG_TYPE_BASKET_ADJUSTMENT = "basket_adjustment" 
LOG_TYPE_STORE_TYPE = "store_type"
LOG_TYPE_BASKET_COMPOSITION = "basket_composition"

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
## Person 
ADULT_AGE_MIN = 18 
ADULT_AGE_MAX = 65 

#-----------------------------------------

EXPERIMENT_NAME = None 
SIMULATION_RUNS = None
SIMULATION_DAYS = None
SIMULATION_OUTPUTFOLDER = None 
SIMULATION_WRITE_TO_FILE_INTERVAL = None
SIMULATION_DEBUG_LOG_ON = None

NH_HOUSES = None
NH_STORE_TYPES = None 
NH_STORE_AMOUNTS = None 

NH_GRID_TRAVEL_TIME_PER_CELL = None 

NH_COOK_SERVINGS_PER_GRAB = None
NH_COOK_INGREDIENTS_PER_QC = None
NH_COOK_MAX_SCALER_COOKING_AMOUNT = None
NH_COOK_EXPIRATION_THRESHOLD = None

HH_AMOUNT_CHILDREN = None
HH_AMOUNT_ADULTS = None
HH_MAX_AVAIL_TIME_PER_DAY = None
HH_IMPULSE_BUY_PERCENTAGE = None
HH_SHOPPING_FREQUENCY = None
HH_MIN_TIME_TO_COOK =  None
HH_PAY_DAY_INTERVAL = None
HH_TIME_PER_STORE = None
HH_DAILY_BUDGET = None
HH_TIME_PER_STORE = None
HH_PRICE_SENSITIVITY = None
HH_BRAND_SENSITIVITY = None
HH_QUALITY_SENSITIVITY = None
HH_AVAILABILITY_SENSITIVITY = None
HH_DEAL_SENSITIVITY = None
HH_PLANNER = None
HH_IMPULSIVITY = None
HH_BRAND_PREFERENCE = None
HH_LEVEL_OF_CONCERN = None

NH_STORE_RESTOCK_INTERVAL = None 
NH_STORE_BASELINE_STOCK = None

STORE_CON_QUALITY = None
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

ADULT_PLATE_WASTE = None 
ADULT_PREFERENCE_VECTOR = None
ADULT_MALE_VEG_SERVINGS = None 
ADULT_MALE_DRY_FOOD_SERVINGS = None 
ADULT_MALE_DAIRY_SERVINGS = None 
ADULT_MALE_MEAT_SERVINGS = None 
ADULT_MALE_SNACKS_SERVINGS = None 
ADULT_MALE_BAKED_SERVINGS = None 
ADULT_MALE_STORE_PREPARED_SERVINGS = None 

ADULT_FEMALE_VEG_SERVINGS = None 
ADULT_FEMALE_DRY_FOOD_SERVINGS = None 
ADULT_FEMALE_DAIRY_SERVINGS = None 
ADULT_FEMALE_MEAT_SERVINGS = None 
ADULT_FEMALE_SNACKS_SERVINGS = None 
ADULT_FEMALE_BAKED_SERVINGS = None 
ADULT_FEMALE_STORE_PREPARED_SERVINGS = None 

CHILD_PLATE_WASTE = None 
CHILD_PREFERENCE_VECTOR = None
CHILD_MALE_VEG_SERVINGS = None 
CHILD_MALE_DRY_FOOD_SERVINGS = None 
CHILD_MALE_DAIRY_SERVINGS = None 
CHILD_MALE_MEAT_SERVINGS = None 
CHILD_MALE_SNACKS_SERVINGS = None 
CHILD_MALE_BAKED_SERVINGS = None 
CHILD_MALE_STORE_PREPARED_SERVINGS = None 

CHILD_FEMALE_VEG_SERVINGS = None 
CHILD_FEMALE_DRY_FOOD_SERVINGS = None 
CHILD_FEMALE_DAIRY_SERVINGS = None 
CHILD_FEMALE_MEAT_SERVINGS = None 
CHILD_FEMALE_SNACKS_SERVINGS = None 
CHILD_FEMALE_BAKED_SERVINGS = None 
CHILD_FEMALE_STORE_PREPARED_SERVINGS = None 

NH_DEALASSESSOR_WEIGHT_SERVING_PRICE = None
NH_BASKETCURATOR_INCREMENT_LIKELIHOOD = None 
NH_BASKETCURATOR_MAX_ITEMS_QUICKSHOP = None

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
    global SIMULATION_RUNS
    global SIMULATION_DAYS
    global SIMULATION_OUTPUTFOLDER
    global SIMULATION_WRITE_TO_FILE_INTERVAL
    global SIMULATION_DEBUG_LOG_ON
    global EXPERIMENT_NAME
    
    global HH_AMOUNT_CHILDREN
    global HH_AMOUNT_ADULTS
    global HH_MAX_AVAIL_TIME_PER_DAY
    global HH_IMPULSE_BUY_PERCENTAGE
    global HH_SHOPPING_FREQUENCY

    global HH_PAY_DAY_INTERVAL
    global HH_TIME_PER_STORE
    global HH_DAILY_BUDGET
    global HH_PRICE_SENSITIVITY
    global HH_BRAND_SENSITIVITY
    global HH_QUALITY_SENSITIVITY
    global HH_AVAILABILITY_SENSITIVITY
    global HH_DEAL_SENSITIVITY
    global HH_PLANNER
    global HH_IMPULSIVITY
    global HH_BRAND_PREFERENCE
    global HH_LEVEL_OF_CONCERN    
    
    global NH_HOUSES
    global NH_STORE_TYPES
    global NH_STORE_AMOUNTS    
    global NH_GRID_TRAVEL_TIME_PER_CELL
    global NH_COOK_SERVINGS_PER_GRAB
    global NH_COOK_INGREDIENTS_PER_QC
    global NH_COOK_MAX_SCALER_COOKING_AMOUNT
    global NH_COOK_EXPIRATION_THRESHOLD
    global NH_STORE_RESTOCK_INTERVAL
    global NH_STORE_BASELINE_STOCK
    
    global STORE_CON_QUALITY
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
    
    global ADULT_PLATE_WASTE
    global ADULT_PREFERENCE_VECTOR
    global ADULT_MALE_VEG_SERVINGS
    global ADULT_MALE_DRY_FOOD_SERVINGS
    global ADULT_MALE_DAIRY_SERVINGS
    global ADULT_MALE_MEAT_SERVINGS
    global ADULT_MALE_SNACKS_SERVINGS 
    global ADULT_MALE_BAKED_SERVINGS
    global ADULT_MALE_STORE_PREPARED_SERVINGS
    
    global ADULT_FEMALE_VEG_SERVINGS
    global ADULT_FEMALE_DRY_FOOD_SERVINGS
    global ADULT_FEMALE_DAIRY_SERVINGS
    global ADULT_FEMALE_MEAT_SERVINGS
    global ADULT_FEMALE_SNACKS_SERVINGS
    global ADULT_FEMALE_BAKED_SERVINGS
    global ADULT_FEMALE_STORE_PREPARED_SERVINGS
    
    global CHILD_PLATE_WASTE
    global CHILD_PREFERENCE_VECTOR
    global CHILD_MALE_VEG_SERVINGS
    global CHILD_MALE_DRY_FOOD_SERVINGS
    global CHILD_MALE_DAIRY_SERVINGS
    global CHILD_MALE_MEAT_SERVINGS
    global CHILD_MALE_SNACKS_SERVINGS
    global CHILD_MALE_BAKED_SERVINGS
    global CHILD_MALE_STORE_PREPARED_SERVINGS
    
    global CHILD_FEMALE_VEG_SERVINGS
    global CHILD_FEMALE_DRY_FOOD_SERVINGS
    global CHILD_FEMALE_DAIRY_SERVINGS
    global CHILD_FEMALE_MEAT_SERVINGS
    global CHILD_FEMALE_SNACKS_SERVINGS
    global CHILD_FEMALE_BAKED_SERVINGS
    global CHILD_FEMALE_STORE_PREPARED_SERVINGS

    global NH_DEALASSESSOR_WEIGHT_SERVING_PRICE
    global NH_BASKETCURATOR_INCREMENT_LIKELIHOOD
    global NH_BASKETCURATOR_MAX_ITEMS_QUICKSHOP
        
    print(file)
    print(os.getcwd())
    with open(file) as f:
        config = json.load(f)
            
    SIMULATION_RUNS = config["Simulation"]["runs"]
    SIMULATION_DAYS = config["Simulation"]["total_days"]
    SIMULATION_OUTPUTFOLDER = config["Simulation"]["output_folder"]
    SIMULATION_WRITE_TO_FILE_INTERVAL = config["Simulation"]["write_to_file_interval"]
    SIMULATION_DEBUG_LOG_ON = config["Simulation"]["debug_log_on"] == "True"
    EXPERIMENT_NAME = config["Simulation"]["name"] 
    
    
    NH_HOUSES = config["Neighborhood"]["nh_houses"]
    store_types = config["Neighborhood"]["nh_store_types"]
    parts = store_types.strip('[]').split(',')
    NH_STORE_TYPES = [part.strip().strip("'") for part in parts]
    NH_STORE_AMOUNTS = [int(item) for item in json.loads(config["Neighborhood"]["nh_store_amounts"])]
    NH_GRID_TRAVEL_TIME_PER_CELL = config["Neighborhood"]["Grid"]["travel_time_per_cell"]
    NH_COOK_SERVINGS_PER_GRAB = config["Neighborhood"]["Cooking"]["cook_servings_per_grab"]
    NH_COOK_INGREDIENTS_PER_QC = config["Neighborhood"]["Cooking"]["cook_ingredients_per_qc"]
    NH_COOK_MAX_SCALER_COOKING_AMOUNT = config["Neighborhood"]["Cooking"]["cook_max_scaler_cooking_amount"]
    NH_COOK_EXPIRATION_THRESHOLD = config["Neighborhood"]["Cooking"]["cook_expiration_threshold"]
    NH_STORE_RESTOCK_INTERVAL = config["Neighborhood"]["Store"]["restock_interval"]
    NH_STORE_BASELINE_STOCK = config["Neighborhood"]["Store"]["baseline_stock"]
    NH_DEALASSESSOR_WEIGHT_SERVING_PRICE = config["Neighborhood"]["DealAssessor"]["weight_serving_price"]
    NH_BASKETCURATOR_INCREMENT_LIKELIHOOD = config["Neighborhood"]["BasketCurator"]["increment_likelihood"]
    NH_BASKETCURATOR_MAX_ITEMS_QUICKSHOP = config["Neighborhood"]["BasketCurator"]["max_items_quickshop"]
    
    
    HH_AMOUNT_CHILDREN =            config["Household"]["hh_amount_children"]
    HH_AMOUNT_ADULTS =              config["Household"]["hh_amount_adults"]
    HH_MAX_AVAIL_TIME_PER_DAY =     config["Household"]["hh_max_avail_time_per_day"]
    HH_IMPULSE_BUY_PERCENTAGE =     config["Household"]["hh_impulse_buy_likelihood"]
    HH_SHOPPING_FREQUENCY =         config["Household"]["hh_shopping_frequency"]
    HH_MIN_TIME_TO_COOK =           config["Household"]["hh_min_time_to_cook"]
    HH_PAY_DAY_INTERVAL =           config["Household"]["hh_pay_day_interval"]
    HH_TIME_PER_STORE =             config["Household"]["hh_time_per_store"]
    HH_DAILY_BUDGET =               config["Household"]["hh_daily_budget"]
    HH_TIME_PER_STORE =             config["Household"]["hh_time_per_store"]
    HH_PRICE_SENSITIVITY =          config["Household"]["hh_price_sensitivity"]
    HH_BRAND_SENSITIVITY =          config["Household"]["hh_brand_sensitivity"]
    HH_QUALITY_SENSITIVITY =        config["Household"]["hh_quality_sensitivity"]
    HH_AVAILABILITY_SENSITIVITY =   config["Household"]["hh_availability_sensitivity"]
    HH_DEAL_SENSITIVITY =           config["Household"]["hh_deal_sensitivity"]
    HH_PLANNER =                    config["Household"]["hh_planner"]
    HH_IMPULSIVITY =                config["Household"]["hh_impulsivity"]
    HH_BRAND_PREFERENCE =           config["Household"]["hh_brand_preference"]
    HH_LEVEL_OF_CONCERN =           config["Household"]["hh_level_of_concern"]
    
    ADULT_PLATE_WASTE = config["Adult"]["adult_plate_waste"]
    ADULT_PREFERENCE_VECTOR = config["Adult"]["adult_preference_vector"]
    ADULT_MALE_VEG_SERVINGS = config["Adult"]["male_veg_servings"]
    ADULT_MALE_DRY_FOOD_SERVINGS = config["Adult"]["male_dry_food_servings"]
    ADULT_MALE_DAIRY_SERVINGS = config["Adult"]["male_dairy_servings"]
    ADULT_MALE_MEAT_SERVINGS = config["Adult"]["male_meat_servings"]
    ADULT_MALE_SNACKS_SERVINGS = config["Adult"]["male_snacks_servings"]
    ADULT_MALE_BAKED_SERVINGS = config["Adult"]["male_baked_servings"]
    ADULT_MALE_STORE_PREPARED_SERVINGS = config["Adult"]["male_store_prepared_servings"]
    ADULT_FEMALE_VEG_SERVINGS = config["Adult"]["female_veg_servings"]
    ADULT_FEMALE_DRY_FOOD_SERVINGS = config["Adult"]["female_dry_food_servings"]
    ADULT_FEMALE_DAIRY_SERVINGS = config["Adult"]["female_dairy_servings"]
    ADULT_FEMALE_MEAT_SERVINGS = config["Adult"]["female_meat_servings"]
    ADULT_FEMALE_SNACKS_SERVINGS = config["Adult"]["female_snacks_servings"]
    ADULT_FEMALE_BAKED_SERVINGS = config["Adult"]["female_baked_servings"]
    ADULT_FEMALE_STORE_PREPARED_SERVINGS = config["Adult"]["female_store_prepared_servings"]
    
    CHILD_PLATE_WASTE                       = config["Child"]["child_plate_waste"]
    CHILD_PREFERENCE_VECTOR                 = config["Child"]["child_preference_vector"]
    CHILD_MALE_VEG_SERVINGS                 = config["Child"]["male_veg_servings"]
    CHILD_MALE_DRY_FOOD_SERVINGS            = config["Child"]["male_dry_food_servings"]
    CHILD_MALE_DAIRY_SERVINGS               = config["Child"]["male_dairy_servings"]
    CHILD_MALE_MEAT_SERVINGS                = config["Child"]["male_meat_servings"]
    CHILD_MALE_SNACKS_SERVINGS              = config["Child"]["male_snacks_servings"]
    CHILD_MALE_BAKED_SERVINGS               = config["Child"]["male_baked_servings"]
    CHILD_MALE_STORE_PREPARED_SERVINGS      = config["Child"]["male_store_prepared_servings"]
    CHILD_FEMALE_VEG_SERVINGS               = config["Child"]["female_veg_servings"]
    CHILD_FEMALE_DRY_FOOD_SERVINGS          = config["Child"]["female_dry_food_servings"]
    CHILD_FEMALE_DAIRY_SERVINGS             = config["Child"]["female_dairy_servings"]
    CHILD_FEMALE_MEAT_SERVINGS              = config["Child"]["female_meat_servings"]
    CHILD_FEMALE_SNACKS_SERVINGS            = config["Child"]["female_snacks_servings"]
    CHILD_FEMALE_BAKED_SERVINGS             = config["Child"]["female_baked_servings"]
    CHILD_FEMALE_STORE_PREPARED_SERVINGS    = config["Child"]["female_store_prepared_servings"]
    
    STORE_CON_QUALITY = config["Store"]["Convenience_store"]["quality"]
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


def log(obj, log_type=None, message="", *args) -> None:
    if SIMULATION_DEBUG_LOG_ON:
        if log_type == LOG_TYPE_TOTAL_SERV and LOG_TYPE_ACTIVE_TOTAL_SERV: 
            _write(obj, message,*args)
        elif log_type == LOG_TYPE_BASKET_ADJUSTMENT and LOG_TYPE_ACTIVE_BASKET_ADJUSTMENT: 
            _write(obj, message,*args)
        elif log_type == LOG_TYPE_DAY_SEPARATOR and LOG_TYPE_ACTIVE_DAY_SEPARATOR: 
            _write(obj, message,*args)
        elif log_type == LOG_TYPE_STORE_TYPE and LOG_TYPE_ACTIVE_STORE_TYPE: 
            _write(obj, message,*args)
        elif log_type == LOG_TYPE_BASKET_COMPOSITION and LOG_TYPE_ACTIVE_BASKET_COMPOSITION: 
            _write(obj, message,*args)
        
def _write(obj, message, *args): 
    if isinstance(message, str) and args:  # Format if message is a string and args are provided
            message = message % args
    else:  # Convert non-string objects to string representation
        message = str(message)
    obj.logger.debug(message)