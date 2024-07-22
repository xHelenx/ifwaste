from threading import local
import pandas as pd

from FoodGroups import FoodGroups 
import globals 

class DealAssessor: 
    def __init__(self) -> None:
        pass
        
    def assess_best_deals(self,stores): 
        #TODO what if a stores does not offer a food group ?!
        
        best_deals = []
             
        for fg in FoodGroups.get_instance().get_all_food_groups():
            options = [] 
            for store in stores: 
                stock_by_fg = store.stock[store.stock["type"] == fg]       
                if not len(stock_by_fg) == 0: #at least one option of fg
                    options.append(stock_by_fg.loc[stock_by_fg["deal_value"].idxmin()])
            if not len(options) == 0: #at least one store carries fg
                options = pd.DataFrame(options).reset_index(drop=True)
                best_deal_by_fg = options.loc[options["deal_value"].idxmin()]
                best_deals.append(best_deal_by_fg)
        if not len(best_deals) == 0:
            best_deals = pd.DataFrame(best_deals).reset_index(drop=True)
        return best_deals
    
    def calculate_deal_value(self,relevant_food_groups, local_deals, best_deals): 
        '''
        relevant_food_groups list of str
        local deals = already multipled value 
        '''
        deal = 0 
        a_1 = globals.DEALASSESSOR_WEIGHT_SERVING_PRICE
        a_2 = 1 - a_1  
        counter = 0
        result = 0
        for fg in relevant_food_groups: 
            if len(best_deals.loc[best_deals["type"] == fg,"deal_value"]) > 0:
                best_deal_value = best_deals.loc[best_deals["type"] == fg,"deal_value"].values[0]
                if len(local_deals.loc[local_deals["type"] == fg,"deal_value"]):
                    local_deal_value = local_deals.loc[local_deals["type"] == fg,"deal_value"].values[0]
                    deal += best_deal_value/local_deal_value
                    counter += 1
        if counter > 0: 
            result = deal/counter
        return result
            
    