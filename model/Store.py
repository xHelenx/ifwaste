from __future__ import annotations  # Delay import for type hints

import math
import random
from numpy import isin
import pandas as pd
import globals
import json

from FoodGroups import FoodGroups
from EnumSales import EnumSales
from EnumStoreTier import EnumStoreTier
from Location import Location

class Store(Location):
    def __init__(self, store_type:EnumStoreTier, grid:Grid, id:int) -> None: # type: ignore
        from Grid import Grid 
        super().__init__(id,grid)
        self.quality:float|None = None 
        self.price:float|None = None 
        self.grid:Grid = grid 
        self.food_groups:FoodGroups = FoodGroups.get_instance()
        self.store_type:EnumStoreTier = store_type
        self.id:int = id
        self.tracker: dict[str,list[int]] = {fg:globals.STORE_MEMORY_LENGTH*[0] for fg in self.food_groups.get_all_food_groups()}
        self.todays_tracker: dict[str,int] = {fg:0 for fg in self.food_groups.get_all_food_groups()}
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
        from StoreLowTier import StoreLowTier 
        from StoreMidTier import StoreMidTier
        if isinstance(other, StoreMidTier) or isinstance(other, StoreLowTier):
            return self.store_type.tier < other.store_type.tier       
    
    def buy_stock(self, amount_per_item:int, fg:str|None=None) -> None: 
        if amount_per_item <= 0:
            return 
        a_1 =  globals.DEALASSESSOR_WEIGHT_SERVING_PRICE
        a_2 = 1- a_1

        to_be_purchased = self.product_range
        if not fg is None: 
            to_be_purchased = self.product_range[self.product_range["type"] == fg]
       
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
        self.todays_tracker =  {fg:0 for fg in self.food_groups.get_all_food_groups()}
        self._plan_and_buy_stock()
        
        #TODO put on sales -> update best_deals_per_fg
        
        
    def do_after_day(self) -> None: 
        self._decay()
        self._throw_out()
        
        
    def _decay(self) -> None:
        self.stock["days_till_expiry"] -= 1
        
    def _throw_out(self) -> None:    
        spoiled_food =  self.stock[self.stock["days_till_expiry"] <= 0] #selected spoiled food to track it
        if len(spoiled_food) > 0:
            self.stock.loc[self.stock["days_till_expiry"] <= 0, "reason"] = globals.FW_SPOILED  
            self._track_removed_from_stock(self.stock.loc[self.stock["days_till_expiry"] <= 0])
            #self.datalogger.append_log(self.id, "log_wasted", location[location["reason"] == globals.FW_SPOILED])   
            self.stock = self.stock[self.stock["days_till_expiry"] > 0] #remove spoiled food 
            
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
    
    def _track_removed_from_stock(self, item:pd.Series | pd.DataFrame, amount:int|None=None)  -> None:
        assert (isinstance(item, pd.Series) and not amount is None) or isinstance(item,pd.DataFrame)
        if isinstance(item,pd.Series):
            self.todays_tracker[item["type"]] += amount # type: ignore
        else:
            for i in item.index: 
                self.todays_tracker[item.loc[i,"type"]] += item.loc[i,"amount"] # type: ignore
                
        
    def _update_tracker(self) -> None: 
        for fg in self.food_groups.get_all_food_groups(): 
            self.tracker[fg] = self.tracker[fg][1:] + [self.todays_tracker[fg]]
    
    def _estimate_needed_stock(self) -> dict[str, int]:
        
        item_per_product = {fg: len(self.product_range[self.product_range["type"] == fg]) 
                if len(self.product_range[self.product_range["type"] == fg]) > 0 
                else 1
                for fg in self.food_groups.get_all_food_groups()}

        
        return {fg : math.ceil(sum(self.tracker[fg])/
                (item_per_product[fg]* globals.STORE_MEMORY_LENGTH))
                for fg in self.food_groups.get_all_food_groups()}
        
    def _plan_and_buy_stock(self) -> None:
        self._update_tracker()
        restock_plan = self._estimate_needed_stock() #dict str float
        for fg in self.food_groups.get_all_food_groups(): 
            if restock_plan[fg] > 0:
                self.buy_stock(restock_plan[fg], fg)
            
        
        