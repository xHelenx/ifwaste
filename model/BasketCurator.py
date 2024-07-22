import pandas as pd
from EnumSales import EnumSales
import globals 
class BasketCurator(): 
    
    def create_basket(self,servings_to_buy_fg, selected_stores, budget):
        basket = pd.DataFrame()
        
        #merge available stocks
        chosen_items = []
        #go over required food groups
        for fg in servings_to_buy_fg[servings_to_buy_fg> 0].index.tolist():
            options = pd.DataFrame()
            for store in selected_stores: 
                if store.is_fg_in_stock(fg): 
                    if len(options) == 0: 
                        options = store.get_stock_of_fg(fg)
                    else: 
                        options = pd.concat([options,store.get_stock_of_fg(fg)], ignore_index=True)
            if len(options) > 0 : 
                items_on_sale = options[options["sale_type"] != EnumSales.NONE] 
                if len(items_on_sale) > 0: 
                    #if items are on sale buy from those (even tho might not be best deal)
                    options = items_on_sale 
                    
            needed_servings = servings_to_buy_fg[fg]
            missing_servings_fg = servings_to_buy_fg
            
           
            while needed_servings > 0: 
                #TODO is ok that chooses fg from different stores?
                if len(options) > 0:
                    plan_to_purchase = options.sample(1,replace=True)
                    options.loc[plan_to_purchase.index[0], "amount"] -= 1
                    
                    plan_to_purchase["amount"] = 1
                    chosen_items.append(plan_to_purchase)
                    options = options[options['amount'] != 0] 
                    needed_servings -= plan_to_purchase["servings"].values[0]
                else:
                    break
            missing_servings_fg[fg] = needed_servings #can be -
            basket = pd.concat(chosen_items, ignore_index=True)
             
        #organize basket
        equal_columns = basket.columns.tolist()
        equal_columns.remove("amount") #TODO 
        basket = basket.groupby(equal_columns, as_index=False)['amount'].sum()
        return (basket, missing_servings_fg)
             
                
    def is_basket_in_budget(self,basket,budget): 
        '''
            returns True/False + budget
        
        '''
        cost = (basket["price_per_serving"] * basket["servings"]).sum()
        return (cost < budget * globals.HH_OVER_BUDGET_FACTOR, budget-cost)
    
    def does_basket_cover_all_fg(self,missing_servings_fg): 
        '''
            returns True/False + missingfgs
        '''
        missing_fgs = missing_servings_fg[missing_servings_fg > 0]   
        return (len(missing_fgs) == 0, missing_fgs.keys())
    
    
    def adjust_basket(self, basket:pd.DataFrame, stores, budget, servings_tracker): 
        (in_budget, left_budget) = self.is_basket_in_budget(basket, budget)
        
        missing_servings_fg = basket.groupby(["type"])["servings"].sum()
        (has_all_req_fg, missing_fgs) = self.does_basket_cover_all_fg(missing_servings_fg)

        basket["adjustment"] = None 
        if not has_all_req_fg:
            (basket, servings_tracker) = self._add_items_from_another_fg(basket,servings_tracker,stores)
            #now has_all_req_fg is still false, but we replaced it with other fgs
        if 
    
    def _add_items_from_another_fg(self, basket, servings_tracker, stores): 
        
        basket = pd.DataFrame()
        chosen_items = []
        options = pd.DataFrame()
        
        #setup available stock
        for store in stores: 
            if len(options) == 0: 
                options = store.store 
            else: 
                options = pd.concat([options,store.stock], ignore_index=True)
            #sales and no sales here
            #buy items (can be larger serving size then needed)
            while servings_tracker["required"].sum()  > servings_tracker["got"].sum() : 
                if len(options) > 0:
                    plan_to_purchase = options.sample(1,replace=True)
                    options.loc[plan_to_purchase.index[0], "amount"] -= 1
                    
                    plan_to_purchase["amount"] = 1
                    chosen_items.append(plan_to_purchase)
                    options = options[options['amount'] != 0] 
                    servings_tracker = self._update_servings_tracker(servings_tracker, plan_to_purchase)
                else:
                    break
            basket = pd.concat(chosen_items, ignore_index=True)
             
        #organize basket
        equal_columns = basket.columns.tolist()
        equal_columns.remove("amount") 
        basket = basket.groupby(equal_columns, as_index=False)['amount'].sum()
        return (basket, servings_tracker)
        
    def _update_servings_tracker(servings_tracker, plan_to_purchase): 
        #update servings in got + is_replacing_other_fg -> this is the replacing fg 
        servings_tracker[plan_to_purchase["type"].values[0]]["got"] += plan_to_purchase["servings"].values[0]
        servings_tracker[plan_to_purchase["type"].values[0]]["is_replacing_other_fg"] += plan_to_purchase["servings"].values[0]
        
        #update servings in is_in_other_fg -> this is the fg that is replaced by another one
        assigned_servings = 0
        while  assigned_servings < plan_to_purchase["servings"].values[0]:
            fgs_missing_servings = servings_tracker[servings_tracker['required'] > servings_tracker['got']]["type"].tolist()
            missing_servings_this_fg = fgs_missing_servings[0]["required"]
            servings = plan_to_purchase["servings"].values[0]
            if missing_servings_this_fg < plan_to_purchase["servings"].values[0]:
                servings = missing_servings_this_fg
            servings_tracker[servings_tracker["type"] == fgs_missing_servings[0]]["is_in_other_fg"] += servings
            assigned_servings + servings 
        
        return servings_tracker 
    
    #def _replace_item_with_cheaper_option(self):
    
    #def _replace_fg_with_cheaper_fg(self):
        
    
    