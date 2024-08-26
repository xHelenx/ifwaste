from Store import Store
import pandas as pd

from FoodGroups import FoodGroups 
import globals 

class DealAssessor: 
    def __init__(self) -> None:
        pass
        
    def assess_best_deals(self,stores:list[Store]) -> pd.DataFrame: 
        """Creates a dataframe with the best deals per food group and their deal value.
        High deal value indicate a bad deal, low values a good deal.

        Args:
            stores (_type_): _description_

        Returns:
            pd.DataFrame: dataframe of items with best deals and their "deal_value" 
        """        
        #TODO what if a store does not offer a food group ?!
        
        best_deals = []
        best_deals_df = pd.DataFrame()   
        for fg in FoodGroups.get_instance().get_all_food_groups(): # type: ignore
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
            best_deals_df = pd.DataFrame(best_deals).reset_index(drop=True)
        return best_deals_df
    
    def calculate_deal_value(self,relevant_food_groups:list[str], local_deals:pd.DataFrame, best_deals:pd.DataFrame) -> float: 
        """Calculates the deal_value for all local deals depending on the best current deals available. Calculates 
        value only for the relevant food groups (relevant because person is considering to buy them).

        Args:
            relevant_food_groups (list[str]): relevant food groups to consider for deal value
            local_deals (pd.DataFrame): current local best deals (local = selected subset of items, intended to be for 1 store)
            best_deals (pd.DataFrame): current best deals over all stores 

        Returns:
            float: normalized deal value of the local deals
        """        
        
        #TODO a_1 and b_2 are not used?!
        
        deal = 0  
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
            
    