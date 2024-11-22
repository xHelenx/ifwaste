import sys
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
        fgs = FoodGroups.get_instance().get_all_food_groups()
        
        best_deals_df = pd.DataFrame({
            "type": fgs,
            "deal_value": sys.float_info.max
        }) 
        for fg in fgs: # type: ignore
            for store in stores: 
                stock_by_fg = store.stock[store.stock["type"] == fg]       
                stock_by_fg.loc[:, "deal_value"] = pd.to_numeric(stock_by_fg["deal_value"])                
                is_better_deal = stock_by_fg["deal_value"].min() < best_deals_df.loc[best_deals_df["type"] == fg,"deal_value"]
                if len(stock_by_fg) > 0 and is_better_deal.values[0]:
                    best_deal_this_fg = stock_by_fg.loc[stock_by_fg["deal_value"].idxmin()]
                    best_deals_df.loc[best_deals_df["type"] == fg,"deal_value"] = best_deal_this_fg["deal_value"]
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
        
        deal = 0  
        counter = 0
        result = 0
        for fg in relevant_food_groups: 
                best_deal_value = best_deals.loc[best_deals["type"] == fg,"deal_value"].values[0]
                local_deal_value = local_deals.loc[local_deals["type"] == fg,"deal_value"].values[0]
                deal += best_deal_value/local_deal_value
                counter += 1
        if counter > 0: 
            result = deal/counter
        return result
            
    