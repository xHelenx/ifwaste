from __future__ import annotations  # Delay import for type hints

import math
import random
from typing import List, Tuple
from numpy import row_stack
import pandas as pd
import globals
import json
import os 

from FoodGroups import FoodGroups
from EnumSales import EnumSales
from EnumStoreTier import EnumStoreTier
from Location import Location
from DiscountEffect import DiscountEffect

class Store(Location):
    def __init__(self, store_type:EnumStoreTier, grid:Grid, id:int) -> None: # type: ignore
        from Grid import Grid 
        super().__init__(id,grid)
        #init through subclass
        self.quality:float|None = None 
        self.price:float|None = None 
        self.high_stock_interval_1:float|None = None
        self.high_stock_interval_2:float|None = None
        self.high_stock_discount_interval_1:float|None = None
        self.high_stock_discount_interval_2:float|None = None
        self.seasonal_likelihood:float|None = None
        self.seasonal_discount:float|None = None
        self.clearance_interval_1:float|None = None
        self.clearance_interval_2:float|None = None
        self.clearance_interval_3:float|None = None
        self.clearance_discount_1:float|None = None
        self.clearance_discount_2:float|None = None
        self.clearance_discount_3:float|None = None
        
        
        
        self.grid:Grid = grid 
        self.food_groups:FoodGroups = FoodGroups.get_instance()
        self.store_type:EnumStoreTier = store_type
        self.id:int = id
        self.product_range:pd.DataFrame = pd.DataFrame()
        with open(globals.CONFIG_PATH) as f: 
            config = json.load(f)
            self.product_range = pd.read_csv(config["Store"][store_type.name]["product_range"])
        self.stock = pd.DataFrame(columns= [
            'type', 
            'servings', 
            'days_till_expiry',
            'price_per_serving',
            'sale_type',
            'amount',
            'deal_value', 
            'store'])      
        
        self.tracker: pd.DataFrame = self.product_range.copy() 
        self.tracker = self.tracker.drop(columns=["price_per_serving"])
        list_init =  [0] * globals.STORE_RESTOCK_INTERVAL
        self.tracker["purchased"] = [list_init[:] for _ in range(len(self.tracker))]
        self.tracker["today"] = 0
        
        
        
        globals.logger_store.debug("All products:")
        globals.logger_store.debug(self.product_range)
    def __str__(self) -> str:
        return self.store_type.name + " at " + str(self.grid.get_coordinates(self))
    
    def __eq__(self, other):
        if isinstance(other, Store):
            if self.grid != None and other.grid != None:
                return self.quality == other.quality and self.price == other.price and\
                    self.grid == other.grid and self.store_type == other.store_type and\
                    self.stock.equals(other.stock) and self.id == other.id 
        return False
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __lt__(self, other) -> bool | None:
        from StoreDiscounterRetailer import StoreDiscounterRetailer 
        from StorePremimumRetailer import StorePremimumRetailer
        if isinstance(other, StorePremimumRetailer) or isinstance(other, StoreDiscounterRetailer):
            return self.store_type.tier < other.store_type.tier       
    
    def buy_stock(self, amount_per_item:int, product:pd.Series | None=None)  -> None: 
        if amount_per_item <= 0:
            return 
        a_1 =  globals.DEALASSESSOR_WEIGHT_SERVING_PRICE
        a_2 = 1- a_1

        to_be_purchased = self.product_range
        if not product is None: 
            to_be_purchased = self.tracker[(self.tracker["type"] == product["type"]) & (self.tracker["servings"] == product["type"])]
            
        for i in to_be_purchased.index: 
            curr_fg = self.food_groups.get_food_group(str(self.product_range.loc[i,"type"]))
            days_till_expiry = random.randint(curr_fg["exp_min"].tolist()[0], curr_fg["exp_max"].tolist()[0]) #TODO only max here
            new_item = {"type": self.product_range.loc[i,"type"], 
                        "servings": self.product_range.loc[i,"servings"],
                        "days_till_expiry": days_till_expiry, #TODO change to gauss
                        "price_per_serving": self.product_range.loc[i,"price_per_serving"],
                        "sale_type": EnumSales.NONE, 
                        "amount" : amount_per_item, 
                        "deal_value": a_1 * self.product_range.loc[i,"price_per_serving"] + a_2 *\
                            self.product_range.loc[i,"price_per_serving"] * self.product_range.loc[i,"servings"],
                        "store": self} 
        
            idx = self.get_idx_of_identical_item_dict(new_item)
            if idx != None:
                self.stock.loc[idx,"amount"] += amount_per_item # type: ignore
            else: 
                new_item = [self.product_range.loc[i,"type"],
                            self.product_range.loc[i,"servings"],
                            days_till_expiry, #TODO entire stock has same expiry date
                            self.product_range.loc[i,"price_per_serving"], 
                            EnumSales.NONE, 
                            amount_per_item,
                            a_1 * self.product_range.loc[i,"price_per_serving"] + a_2 *\
                            self.product_range.loc[i,"price_per_serving"] * self.product_range.loc[i,"servings"],
                            self]
                    
                self.stock.loc[len(self.stock)] = new_item    
                                        
    def get_idx_of_identical_item_df(self,item:pd.Series) -> int | None : #returns item or none
        """Takes a stock item and returns stock item with the same characteristics
        (besides amount). Helper function to manipulate stock items. 

        Args:
            item (pd.Series): _description_

        Returns:
            pd.Dataframe: selected row that matches the item attributes, if none matches
            returns None 
        """        
        mask =  (self.stock["type"] == item["type"]) & (self.stock["servings"] == item["servings"]) &\
            (self.stock["days_till_expiry"] == item["days_till_expiry"]) & (self.stock["sale_type"] == item["sale_type"]) &\
            (self.stock["store"] == item["store"])
        if len(self.stock.index[mask].tolist())> 0: 
            return self.stock.index[mask].tolist()[0]
        else:
            return None
             
    def get_idx_of_identical_item_dict(self,item)-> int | None :  #returns item or none
        mask =  (self.stock["type"] == item["type"]) & (self.stock["servings"] == item["servings"]) &\
            (self.stock["days_till_expiry"] == item["days_till_expiry"]) & (self.stock["sale_type"] == item["sale_type"]) &\
            (self.stock["store"] == item["store"])
        if len(self.stock.loc[mask].index) > 0: 
            return self.stock.loc[mask].index[0]
        else:
            return None
    
    def is_fg_in_stock(self, fg) -> bool: 
        return fg in self.stock["type"].unique()
    
    def do_before_day(self) -> None: 
        globals.logger_store.debug("---- DAY %i ----",  globals.DAY )
        globals.logger_store.debug(self.stock)

        
        if globals.DAY == 0:  #on first day stock store with baseline amount
            self.buy_stock(amount_per_item=globals.STORE_BASELINE_STOCK)
        else: #from them on restock based on demand
            self.tracker["today"] = 0 #reset amount tracker for today
            self._plan_and_buy_stock()
            self._update_sales()
        
            #TODO put on sales -> update best_deals_per_fg
            
        
        
    def do_after_day(self) -> None: 
        self._decay()
        self._throw_out()
        self._update_tracker() #shift todays value into memory
        
        
    def _decay(self) -> None:
        self.stock["days_till_expiry"] -= 1
        
    def _throw_out(self) -> None:    
        spoiled_food =  self.stock[self.stock["days_till_expiry"] <= 0] #selected spoiled food to track it
        if len(spoiled_food) > 0:
            self.stock.loc[self.stock["days_till_expiry"] <= 0, "reason"] = globals.FW_SPOILED  
            for index, item in self.stock.loc[self.stock["days_till_expiry"] <= 0].iterrows():
                self._track_removed_from_stock(item=item,amount=item["amount"])
            #self.datalogger.append_log(self.id, "log_wasted", location[location["reason"] == globals.FW_SPOILED])   
            self.stock = self.stock[self.stock["days_till_expiry"] > 0] #remove spoiled food 
            self.stock = self.stock.drop(columns=["reason"])
            
    def get_stock_of_fg(self,fg) -> pd.DataFrame:
        return self.stock[self.stock["type"]==fg]
    
    def get_available_food_groups(self) -> list[str]:
        '''
        generally available in product range, hh doesnt know if it is not in stock
        '''
        return self.product_range["type"].unique().tolist()
    
    def is_fg_in_productrange(self, fg) -> bool: 
        return fg in self.product_range["type"].unique().tolist()
    
    def organize_stock(self) -> None: 
        """Removes all products from stock, that are sold out (amount=0)
        """        
        self.stock = self.stock[self.stock["amount"] > 0]
        
    def buy(self,item:pd.Series,amount:int=1) -> None:
        """Purchases an number of items from the store. Reduces the stock
        and returns a tuple with a) how many items were available to buy as well as 
        b) the price for the purchase.

        Args:
            item (pd.DataFrame): item to be bought
            amount (int, optional): Number of items to be bought. Defaults to 1.

        Returns:
            tuple: a) how many items were bought, b) summed price
        """         
        idx = self.get_idx_of_identical_item_df(item)
        assert self.stock.loc[idx,"amount"] >= amount # type: ignore
        self.stock.loc[idx,"amount"] -= amount  # type: ignore
        self._track_removed_from_stock(item,amount)
        
    def give_back(self,item: pd.Series,amount:int) -> None: 
        """Returns an item back to the store. Store puts it back in stock 
        and returns the expense for the items

        Args:
            item (pd.Series): _description_
            amount (int): _description_

        Returns:
            expense (float): Expenses of returned food items
        """        
        idx = self.get_idx_of_identical_item_df(item)
        if idx != None: #add to existing entry
            self.stock.loc[idx,"amount"] += amount # type: ignore
        else: #create new entry
            item["amount"] = amount
            self.stock = pd.concat([self.stock, item])
        self._track_removed_from_stock(item,-amount)
    
    def _track_removed_from_stock(self, item:pd.Series, amount:int|None=None)  -> None:
        assert (isinstance(item, pd.Series) and not amount is None) or isinstance(item,pd.DataFrame)
        mask = (self.tracker["type"] == item["type"]) & (self.tracker["servings"] == item["servings"])
        self.tracker.loc[mask, "today"] += amount
        
    def _update_tracker(self) -> None: 
        self.tracker["purchased"] = self.tracker.apply(lambda row: row["purchased"][1:] + [row["today"]], axis=1)

    def _plan_and_buy_stock(self) -> None:
        globals.logger_store.debug("Tracker:")
        globals.logger_store.debug(self.tracker)
        restock_plan = self.tracker["purchased"].sum()
        globals.logger_store.debug("PLANNED STOCK:")
        globals.logger_store.debug(restock_plan)
        for index, row in self.tracker.iterrows():
            self.buy_stock(restock_plan[index], row)
        
    def _update_sales(self,): 
        #self._remove_ended_sales() 
        self._start_sales()
        
    def _remove_ended_sales(self): 
        #remove seasonal sales, that timed out
        mask = (self.stock["sale_timer"] == 0) & (self.stock["sale_type"] == EnumSales.SEASONAL)
        
        #iterate over all discount effects
        for discount_effect in DiscountEffect: 
            self.stock.loc[mask & (self.stock["discount_effect"] == discount_effect),"servings"] = (self.stock["servings"] / discount_effect.scaler)
        
        self.stock.loc[mask,"sale_type"] = EnumSales.NONE
        self.stock.loc[(self.stock["sale_timer"] == 0) & (self.stock["sale_type"] == EnumSales.NONE),"discount_effect"] =  DiscountEffect.NONE
        
    def _start_sales(self):
        self.stock["sale_option"] = [] * len(self.stock)
        for _,row in self.product_range.iterrows(): 
            #select all items of this product type
            mask = (self.stock["type"] == row["type"]) & (self.stock["servings"] == row["servings"])
            current_product = self.stock[mask]
            ## high stock sales ##
            if current_product["amount"][0] >= globals.STORE_BASELINE_STOCK * self.high_stock_interval_2:
                self._add_sales_options([(EnumSales.HIGHSTOCK, [self.high_stock_discount_interval_2])])                
            elif current_product["amount"]  >= globals.STORE_BASELINE_STOCK * self.high_stock_interval_1:
                self._add_sales_options( [(EnumSales.HIGHSTOCK, [self.high_stock_discount_interval_1])])
            ## clearance sales ## 
            for _,row_by_exp in self.stock[mask].iterrows():
                #select all item of 1 expiry date
                if row_by_exp["days_till_expiry"] <= self.clearance_interval_3: 
                    self._add_sales_options([EnumSales.EXPIRING,self.clearance_discount_3])
                elif row_by_exp["days_till_expiry"] <= self.clearance_interval_2: 
                    self._add_sales_options([EnumSales.EXPIRING,self.clearance_discount_2])
                elif row_by_exp["days_till_expiry"] <= self.clearance_interval_1: 
                    self._add_sales_options([EnumSales.EXPIRING,self.clearance_discount_1])  
                              
            ## seasonal sales (random sales)
            if random.uniform(0,1) < self.likelihood_seasonal:  # type: ignore
                self._add_sales_options([EnumSales.SEASONAL,self.seasonal_discount])  
                
            globals.logger_store.debug("Sales options have been added:")
            globals.logger_store.debug(self.stock)
            
            
            
                
        #what if it is on sale already - skip
        
     #   if item["sale_type"] == EnumSales.NONE: 
                #TODO update sale
     #   else: 
            
    def _add_sales_options(self,item:List[Tuple(EnumSales,List)]): 
        #add item to the temporary list of possible sales to apply to the item 
        self.stock['sale_option'] = self.stock['sale_option'].apply(lambda x: x + item)