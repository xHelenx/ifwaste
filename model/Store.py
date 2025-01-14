from __future__ import annotations  # Delay import for type hints

import hashlib
from logging import Logger
import math
import random
from typing import Hashable, List, Literal, Optional, Tuple, Union
from numpy import row_stack
import pandas as pd
import globals
import json
import os 

from FoodGroups import FoodGroups
from EnumSales import EnumSales
from EnumStoreTier import EnumStoreTier
from Location import Location
from EnumDiscountEffect import EnumDiscountEffect

class Store(Location):
    def __init__(self, store_type:EnumStoreTier, grid:Grid, id:int) -> None: # type: ignore
        from Grid import Grid 
        
        
        #debug
        self.sold_today = 0
        self.allowed_cols = {"type", "servings", "days_till_expiry", "price_per_serving", "sale_type", "discount_effect",
                                  "deal_value", "sale_timer", "store", "product_ID", "amount"}
        
        
        super().__init__(id,grid)
        #init through subclass
        self.quality:float|None = None 
        self.price:float|None = None 
        self.high_stock_interval_1:float|None = None
        self.high_stock_interval_2:float|None = None
        self.high_stock_discount_1:list[EnumDiscountEffect] = []
        self.high_stock_discount_2:list[EnumDiscountEffect] = []
        self.seasonal_likelihood:float|None = None
        self.seasonal_discount:list[EnumDiscountEffect] = []
        self.seasonal_duration:float|None = None
        self.clearance_interval_1:float|None = None
        self.clearance_interval_2:float|None = None
        self.clearance_interval_3:float|None = None
        self.clearance_discount_1:list[EnumDiscountEffect] = []
        self.clearance_discount_2:list[EnumDiscountEffect] = []
        self.clearance_discount_3:list[EnumDiscountEffect] = []
        
        self.grid:Grid = grid 
        self.food_groups:FoodGroups = FoodGroups.get_instance()
        self.store_type:EnumStoreTier = store_type
        self.id:int = id
        self.product_range:pd.DataFrame = pd.DataFrame()
        with open(globals.CONFIG_PATH) as f: 
            config = json.load(f)
            self.product_range = pd.read_csv(config["Store"][store_type.value]["product_range"])
            self.product_range["product_ID"] = self.product_range.apply(lambda x: str(x["type"]) + str(x["servings"]) + str(x["price_per_serving"]), axis=1)        
            self.stock = pd.DataFrame(columns= [
            'type', 
            'servings', 
            'days_till_expiry',
            'price_per_serving',
            'sale_type',
            'discount_effect',
            'amount',
            'deal_value', 
            'sale_timer',
            'store',
            'product_ID'])      
        
        self.tracker: pd.DataFrame = self.product_range.copy() 
        self.tracker = self.tracker.drop(columns=["price_per_serving", "type", "servings"])
        list_init =  [0] * globals.STORE_RESTOCK_INTERVAL
        self.tracker["purchased"] = [list_init[:] for _ in range(len(self.tracker))]
        self.tracker["today"] = 0
        self.price = self.product_range["price_per_serving"].mean()
        self.logger: Logger|None= globals.setup_logger( str(self.store_type.name)+ str(self.id))
        
    def __str__(self) -> str:
        return self.store_type.value + " at " + str(self.grid.get_coordinates(self))
    
    def __eq__(self, other):
        if isinstance(other, Store):
            if self.grid != None and other.grid != None:
                return self.store_type == other.store_type and self.id == other.id 
        return False
    

    def __lt__(self, other:Store):
        if not isinstance(other, Store):
            return NotImplemented
        return self.store_type.name < other.store_type.name  # Compare based on name (or any other attribute)
    
    def __hash__(self) -> int:
        return hash(self.id)  
    
    def buy_stock(self, amount_per_item:int, product:pd.Series | None=None)  -> None: 
        if amount_per_item <= 0:
            return 
        a_1 =  globals.DEALASSESSOR_WEIGHT_SERVING_PRICE
        a_2 = 1- a_1
        
        to_be_purchased = self.product_range
        if product is not None: 
            to_be_purchased = self.tracker[self.tracker["product_ID"] == product["product_ID"]]
            
        for i in to_be_purchased.index: 
            #for each item that is bought, init a new item
            curr_fg = self.food_groups.get_food_group(str(self.product_range.loc[i,"type"]))
            days_till_expiry = random.randint(curr_fg["exp_min"].tolist()[0], curr_fg["exp_max"].tolist()[0]) #TODO only max here
            new_item = {"type": self.product_range.loc[i,"type"], 
                        "servings": self.product_range.loc[i,"servings"],
                        "days_till_expiry": days_till_expiry, #TODO change to gauss
                        "price_per_serving": self.product_range.loc[i,"price_per_serving"],
                        "sale_type": EnumSales.NONE, 
                        "discount_effect": EnumDiscountEffect.NONE,
                        "amount" : amount_per_item, 
                        "deal_value": a_1 * self.product_range.loc[i,"price_per_serving"] + a_2 *\
                            self.product_range.loc[i,"price_per_serving"] * self.product_range.loc[i,"servings"],
                        "sale_timer": globals.SALES_TIMER_PLACEHOLDER,
                        "store": self,
                        "product_ID": str(self.product_range.loc[i,"type"]) + str(self.product_range.loc[i,"servings"])+ \
                        str(self.product_range.loc[i,"price_per_serving"])}      
            new_item = pd.Series(new_item)
            idx = self.get_item_index(new_item)     
            #check if the exact item specs. already exist -> then just add amount instead
            if idx is not None:
                self.stock.loc[idx,"amount"] += amount_per_item # type: ignore
                assert set(self.stock.columns).issubset(self.allowed_cols), f"Unexpected column detected: {set(self.stock.columns) - self.allowed_cols}"

            else: #else add it as new item 
                new_item = new_item.reindex(self.stock.columns, fill_value=None) 
                self.stock = pd.concat([self.stock, pd.DataFrame([new_item])], ignore_index=True)                  
                assert set(self.stock.columns).issubset(self.allowed_cols), f"Unexpected column detected: {set(self.stock.columns) - self.allowed_cols}"
            globals.log(self,new_item.to_frame().T)
            self.organize_stock()

    def get_item_index(self, item:pd.Series) -> int | None: 
        """Takes a stock item and returns stock item with the same characteristics
        (besides amount). Helper function to manipulate stock items. 

        Args:
            item (pd.Series): _description_

        Returns:
            pd.Dataframe: selected row that matches the item attributes, if none matches
            returns None 
        """      
        self.stock = self.stock.reset_index(drop=True)
        if len(self.stock) > 0:
            indices =  self.stock[
                (self.stock["type"] == item.type)
                & (self.stock["servings"] == item.servings)
                & (self.stock["days_till_expiry"] == item.days_till_expiry)
                & (self.stock["price_per_serving"] == item.price_per_serving)
                & (self.stock["sale_type"] == item.sale_type)
                & (self.stock["discount_effect"] == item.discount_effect)
                & (self.stock["sale_timer"] == item.sale_timer)
                & (self.stock["store"] == item.store)
                & (self.stock["product_ID"] == item.product_ID)            
                ].index
        else:
            return None
            
        return indices[0] if not indices.empty else None # type: ignore
    
    def is_fg_in_stock(self, fg:str) -> bool: 
        return fg in self.stock["type"].unique()
    
    def _debug_amount(self, df:pd.DataFrame) -> int: 
        non_bogo = df.loc[df["discount_effect"] != EnumDiscountEffect.BOGO, "amount"].sum()
        bogo = df.loc[df["discount_effect"] == EnumDiscountEffect.BOGO, "amount"].sum() * 2
    
        return non_bogo + bogo
    def do_before_day(self) -> None:    
        self.sold_today = 0
        globals.log(self,"---- DAY %i ----",  globals.DAY )
        globals.log(self, "ITEMS IN STOCK: %i", self._debug_amount(self.stock))
        
        if globals.DAY == 0:  #on first day stock store with baseline amount
            self.buy_stock(amount_per_item=globals.STORE_BASELINE_STOCK)
            #globals.log(self,"--- after restocking ---" )
            #globals.log(self,self.stock)
        else: #from them on restock based on demand
            self.tracker["today"] = 0 #reset amount tracker for today
            self._plan_and_buy_stock()
            self._manage_sales()
            #globals.log(self,"--- after restocking and sales ---" )
            #globals.log(self,self.stock)

            
    def do_after_day(self) -> None: 
        self._decay()
        self._throw_out()
        self._update_tracker() #shift todays purchase value into memory
        
        mask  = self.stock["sale_type"] == EnumSales.SEASONAL #all seasonal items      
        self.stock.loc[mask,"sale_timer"] -= 1 #a day passed -> reduce time till sales ends        
        self.organize_stock()
        globals.log(self, "ITEMS SOLD: %i", self.sold_today)
        globals.log(self, "Tracker:")
        globals.log(self, self.tracker)

        
        
    def _decay(self) -> None:
        self.stock["days_till_expiry"] -= 1
        
    def _throw_out(self) -> None:    
        spoiled_food =  self.stock[self.stock["days_till_expiry"] <= 0.0] #selected spoiled food to track it
        globals.log(self, "ITEMS THROWN OUT: %i", self._debug_amount(spoiled_food))

        if len(spoiled_food) > 0:
            self.stock.loc[self.stock["days_till_expiry"] <= 0.0, "reason"] = globals.FW_SPOILED  
            for _, item in self.stock.loc[self.stock["days_till_expiry"] <= 0.0].iterrows():
                self._track_removed_from_stock(item=item,amount=item["amount"])
            #self.datalogger.append_log(self.id, "log_wasted", location[location["reason"] == globals.FW_SPOILED])   
            #self.stock = self.stock[self.stock["days_till_expiry"] > 0.0] #remove spoiled food 
            self.stock.drop(spoiled_food.index, inplace=True)  # remove expired 
            self.stock = self.stock.drop(columns=["reason"])
    
    def get_available_food_groups(self) -> list[str]:
        '''
        generally available in product range, hh doesnt know if it is not in stock
        '''
        return self.product_range["type"].unique().tolist()
    
    def is_fg_in_product_range(self, fg) -> bool: 
        return fg in self.product_range["type"].unique().tolist()
    
    def organize_stock(self) -> None:
        """Removes all products from stock that are sold out (amount=0) and groups the remaining items."""
        
        self.stock = self.stock[self.stock["amount"] > 0]

        # Convert enums to strings temporarily for grouping
        self.stock["sale_type"] = self.stock["sale_type"].apply(lambda x: str(x))
        self.stock["discount_effect"] = self.stock["discount_effect"].apply(lambda x: str(x))

        # Perform grouping and aggregation
        self.stock = (
            self.stock.groupby(
                [
                    "type", "servings", "days_till_expiry", "price_per_serving",
                    "sale_type", "discount_effect", "deal_value",
                    "sale_timer", "store", "product_ID"
                ],
                as_index=False
            )
            .agg({
                "amount": "sum"  # Sum up the amounts
            }) # type: ignore
        ) # type: ignore

        # Convert strings back to Enums
        self.stock["sale_type"] = self.stock["sale_type"].map(lambda x: globals.to_EnumSales(x)) # type: ignore
        self.stock["discount_effect"] = self.stock["discount_effect"].map(lambda x: globals.to_EnumDiscountEffect(x)) # type: ignore
        assert set(self.stock.columns).issubset(self.allowed_cols), f"Unexpected column detected: {set(self.stock.columns) - self.allowed_cols}"

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
        idx = self.get_item_index(item)
        assert self.stock.loc[idx,"amount"] >= amount # type: ignore
        self.stock.loc[idx,"amount"] -= amount  # type: ignore
        self._track_removed_from_stock(item,amount)
        
        if item["discount_effect"] == EnumDiscountEffect.BOGO: 
            amount *= 2 
        self.sold_today += amount
        
        assert set(self.stock.columns).issubset(self.allowed_cols), f"Unexpected column detected: {set(self.stock.columns) - self.allowed_cols}"
        
    def give_back(self,item: pd.Series,amount:int) -> None: 
        """Returns an item back to the store. Store puts it back in stock 
        and returns the expense for the items

        Args:
            item (pd.Series): _description_
            amount (int): _description_

        Returns:
            expense (float): Expenses of returned food items
        """        
        idx = self.get_item_index(item)
        
        if "impulse_buy_likelihood" in item.index:
            item = item.drop(labels=["impulse_buy_likelihood"])
        
        if idx != None: #add to existing entry
            self.stock.loc[idx,"amount"] += amount # type: ignore
            assert set(self.stock.columns).issubset(self.allowed_cols), f"Unexpected column detected: {set(self.stock.columns) - self.allowed_cols}"
        else: #create new entry
            item["amount"] = amount
            self.stock = pd.concat([self.stock, pd.DataFrame([item])])
            assert set(self.stock.columns).issubset(self.allowed_cols), f"Unexpected column detected: {set(self.stock.columns) - self.allowed_cols}"
        self._track_removed_from_stock(item,-amount)
        if item["discount_effect"] == EnumDiscountEffect.BOGO: 
            amount *= 2 
        self.sold_today -= amount
    
    def _track_removed_from_stock(self, item:pd.Series, amount:int|None=None)  -> None:
        assert (isinstance(item, pd.Series) and not amount is None) or isinstance(item,pd.DataFrame)
        mask = (self.tracker["product_ID"] == item["product_ID"]) #here product not item 
        
        if item["discount_effect"] == EnumDiscountEffect.BOGO: 
            amount *= 2 
            
        self.tracker.loc[mask, "today"] += amount  
        
    def _update_tracker(self) -> None: 
        self.tracker["purchased"] = self.tracker.apply(lambda row: row["purchased"][1:] + [row["today"]], axis=1)

    def _plan_and_buy_stock(self) -> None:
        if globals.DAY % globals.STORE_RESTOCK_INTERVAL == 0:       
            self.tracker["planned_restock_amount"] = self.tracker["purchased"].apply(lambda x: sum(x))
            globals.log(self, "ITEMS TO RESTOCK: %i", self.tracker["planned_restock_amount"].sum())
            for index, row in self.tracker.iterrows():
                self.buy_stock(self.tracker.loc[index, "planned_restock_amount"], row) # type: ignore
            self.tracker["planned_restock_amount"] = self.tracker["purchased"].apply(lambda x: 0)
            
    def _manage_sales(self,) -> None: 
        #remove finished sales (clearance automatically when food is bad/bought)
        self._update_seaonsal_sales()
        self._update_high_stock_sales()
        self._update_clearance_sales()
        self._add_new_sales()
        
    def _update_clearance_sales(self) -> None: 
        mask = (self.stock["sale_type"] == EnumSales.EXPIRING)

        for idx,row in self.stock[mask].iterrows(): 
            if row["days_till_expiry"] <= self.clearance_interval_3 and \
            (row["discount_effect"] not in self.clearance_discount_3):
                #1. if item is below interval 1 and was one sale-> back to original price
                self._change_sale(idx,new_sale_options=self.clearance_discount_3)
                
            elif row["days_till_expiry"] > self.clearance_interval_3 and \
                row["days_till_expiry"] <= self.clearance_interval_2 and \
                (row["discount_effect"] not in self.clearance_discount_2):
                #1. if item is below interval 1 and was one sale-> back to original price
                self._change_sale(idx,new_sale_options=self.clearance_discount_2)
                
            elif row["days_till_expiry"] > self.clearance_interval_2 and \
                row["days_till_expiry"] <= self.clearance_interval_1 and \
                (row["discount_effect"] not in self.clearance_discount_1):
                #1. if item is below interval 1 and was one sale-> back to original price
                self._change_sale(idx,new_sale_options=self.clearance_discount_1)           
    
                            
    def _update_seaonsal_sales(self) -> None: 
        #remove seasonal sales, that timed out
        mask = (self.stock["sale_timer"] == 0) & (self.stock["sale_type"] == EnumSales.SEASONAL)
        self._change_sale(mask, new_sale_options=None) #remove item
        
        
    def _change_sale(self, mask_or_index: Union[pd.Series, Hashable], new_sale_options: Optional[list] = None, all_same_sale_type: bool = True) -> None:
        """
        Change sale options for items in stock.
        
        Parameters:
            mask_or_index (Union[pd.Series, int]): Boolean mask or row index specifying which rows to update.
            new_sale_options (Optional[list]): New sale options to apply.
            all_same_sale_type (bool): Whether to apply the same sale type to all items.
        """
        # Determine if we are using a mask (batch operation) or single index (row-specific operation)
        if isinstance(mask_or_index, pd.Series) and mask_or_index.any():  # Mask provided, check if any items match
            selected_rows = self.stock.loc[mask_or_index]
        elif isinstance(mask_or_index, int):  # Single row index provided
            selected_rows = self.stock.loc[[mask_or_index]]
        else:
            return  # no rows selected

        # Get unique discounts in place
        discounts_in_place = selected_rows["discount_effect"].unique()
        if EnumDiscountEffect.NONE in discounts_in_place:
            discounts_in_place = discounts_in_place[discounts_in_place != EnumDiscountEffect.NONE]

        # Remove old sale details
        sale_type = selected_rows["sale_type"].iloc[0]
        self.stock.loc[selected_rows.index, "sale_type"] = EnumSales.NONE # type: ignore
        self.stock.loc[selected_rows.index, "discount_effect"] = EnumDiscountEffect.NONE # type: ignore
        self.stock.loc[selected_rows.index, "sale_timer"] = globals.SALES_TIMER_PLACEHOLDER
        discount_effect = discounts_in_place[0] if len(discounts_in_place) > 0 else EnumDiscountEffect.NONE

        # Reverse previous discount effect
        if discount_effect == EnumDiscountEffect.BOGO:
            self.stock.loc[selected_rows.index, "servings"] /= discount_effect.scaler
            self.stock.loc[selected_rows.index, "price_per_serving"] *= discount_effect.scaler
            self.stock.loc[selected_rows.index, "amount"] *= discount_effect.scaler
        else:
            self.stock.loc[selected_rows.index, "price_per_serving"] /= discount_effect.scaler

        # Apply new sale options if provided
        if new_sale_options:
            if all_same_sale_type:
                self._add_sale_to_item(mask_or_index, sale_type, new_sale_options)
            else:
                for row_index in selected_rows.index:
                    self._add_sale_to_item(row_index, sale_type, new_sale_options)

        # Update deal values
        self._update_deal_value()

    
    def handle_bogo_per_row(self,row:pd.Series, discount_scaler) -> list[pd.Series]:
        ##Important pass a copy of the item?
        if row["amount"] % discount_scaler == 0: #even number -> easy - apply bogo rules
            row["amount"] //= discount_scaler
            row["servings"] *= discount_scaler
            row["price_per_serving"] /= discount_scaler
            return [row]
        elif row["amount"] > 1: #make sure there is not just 1 and it create an empty row
            #split into row that applies bogo for as many items as possible + leftover row
            no_bogo = row.copy()
            bogo = row.copy()
            
            bogo["amount"] //= discount_scaler
            bogo["servings"] *= discount_scaler
            bogo["price_per_serving"] /= discount_scaler
            
            no_bogo["amount"] = row["amount"] % discount_scaler   
            no_bogo["sale_type"] = EnumSales.NONE
            no_bogo["discount_effect"] = EnumDiscountEffect.NONE
            return [bogo,no_bogo]
        else:
            return [row]
    
    def _add_sale_to_item(self,mask, sale_type, discount_effects) -> None:  
        selected_discount_effect = random.choice(discount_effects) # type: ignore
        self.stock.loc[mask, "sale_type"] = sale_type
        self.stock.loc[mask, "discount_effect"] = selected_discount_effect
        if selected_discount_effect == EnumDiscountEffect.BOGO: 
            result_rows = []
            if not isinstance(mask, int): #more than 1 row     

                result_rows = [
                            processed_row
                            for _, row in self.stock.loc[mask].iterrows()
                            for processed_row in self.handle_bogo_per_row(row.copy(deep=True), row["discount_effect"].scaler)
                ]
                self.stock = self.stock[~mask]
            else: 
                result_rows = self.handle_bogo_per_row(self.stock.iloc[mask].copy(deep=True), self.stock.loc[mask,"discount_effect"].scaler)  # type: ignore
                self.stock = self.stock[~self.stock.index.isin([mask])]
                         
            self.stock = pd.concat([self.stock, pd.DataFrame(result_rows)], ignore_index=True)
            self.stock = self.stock.reset_index(drop=True)
        else: 
            self.stock.loc[mask, "price_per_serving"]  *= selected_discount_effect.scaler
            
    def _update_high_stock_sales(self): 
        #update high stock items that are already on sale
        for _, row in self.product_range.iterrows():
            # Select the actual product from the product range (all items that match)
            mask = (self.stock["product_ID"] == row["product_ID"])
            high_stock_mask =  self.stock.loc[mask, "sale_type"] == EnumSales.HIGHSTOCK
            
            if high_stock_mask.any(): # type: ignore
                # At least some of the items have already been decided to go on highstock sale (might have new shipment that is missing)
                total_amount = self.stock.loc[mask, "amount"].sum() # type: ignore
                if (total_amount <= globals.STORE_BASELINE_STOCK * self.high_stock_interval_1) and \
                (self.stock.loc[mask,"discount_effect"].iloc[0] not in self.high_stock_discount_1): # type: ignore #I can check the first here, cause they are all on the same deal
                    # 1. If item is below interval 1 and was on sale -> back to original price
                    self._change_sale(mask & (high_stock_mask))
                
                elif globals.STORE_BASELINE_STOCK * self.high_stock_interval_1 < total_amount <= globals.STORE_BASELINE_STOCK * self.high_stock_interval_2  and \
                (self.stock.loc[mask,"discount_effect"].iloc[0] not in self.high_stock_discount_2): # type: ignore
                    # 2. It's between interval 1 and interval 2 -> apply di scount for interval 1
                    # Ignore if BOGO, if sales, revert old discount, apply new discount
                    self._change_sale(mask & (high_stock_mask), new_sale_options=self.high_stock_discount_1)
                
                elif total_amount > globals.STORE_BASELINE_STOCK * self.high_stock_interval_2 and \
                (self.stock.loc[mask,"discount_effect"].iloc[0] not in self.high_stock_discount_2): # type: ignore
                    # 3. Items that shifted from interval 1 to interval 2
                    # Ignore if BOGO, if sales, revert old discount, apply new discount
                    self._change_sale(mask & (high_stock_mask), new_sale_options=self.high_stock_discount_2)

   
    def _add_new_sales(self):
        ## determine all possible sales for each item
        self.stock["sale_option"] = [[] for _ in range(len(self.stock))]
        for _,row in self.product_range.iterrows(): 
            #select all items of this product type
            mask = (self.stock["product_ID"] == row["product_ID"])
            current_product = self.stock[mask]
            ## high stock sales ##
            mask_no_sale_applied = mask & (self.stock["sale_type"] == EnumSales.NONE)
            if current_product["amount"].sum() >= globals.STORE_BASELINE_STOCK * self.high_stock_interval_2:
                self._add_sales_options(mask_no_sale_applied,[(EnumSales.HIGHSTOCK, self.high_stock_discount_2)])                
            elif current_product["amount"].sum()  >= globals.STORE_BASELINE_STOCK * self.high_stock_interval_1:
                self._add_sales_options(mask_no_sale_applied, [(EnumSales.HIGHSTOCK, self.high_stock_discount_1)])
           
           #now we look at each item of this product type (could vary by e.g. expiry date)
            for _,row_by_exp in self.stock[mask_no_sale_applied].iterrows():
                ## clearance sales ## 
                #select all item of 1 expiry date
                if row_by_exp["days_till_expiry"] <= self.clearance_interval_3: 
                    self._add_sales_options(mask,[(EnumSales.EXPIRING,self.clearance_discount_3)])
                elif row_by_exp["days_till_expiry"] <= self.clearance_interval_2: 
                    self._add_sales_options(mask,[(EnumSales.EXPIRING,self.clearance_discount_2)])
                elif row_by_exp["days_till_expiry"] <= self.clearance_interval_1: 
                    self._add_sales_options(mask,[(EnumSales.EXPIRING,self.clearance_discount_1)])
                              
                ## seasonal sales (random sales)
                if random.uniform(0,1) < self.seasonal_likelihood:  # type: ignore
                    self._add_sales_options(mask,[(EnumSales.SEASONAL,self.seasonal_discount)])        
          
        #all items that are empty are set to NONE:         
        self.stock['sale_option'] = self.stock['sale_option'].apply(lambda x: [(EnumSales.NONE,[EnumDiscountEffect.NONE])] if len(x) == 0 else x)

        ## select a random sale and apply it  
        self._apply_sales()   

    def _apply_sales(self): 
        #all sale options have been slected in sale_options -> now we choose one
        #choose sale and apply it
        
        mask = (self.stock["sale_type"] == EnumSales.NONE) & ~self.stock["sale_option"].apply( \
            lambda x: x == [(EnumSales.NONE, [EnumDiscountEffect.NONE])])

        idx = self.stock.loc[mask].index
         
        if self.stock["sale_option"].apply(lambda x: x != [(EnumSales.NONE, [EnumDiscountEffect.NONE])]).any():  
            self.stock.loc[idx,'sale_option'] = self.stock.loc[idx,'sale_option'].apply(lambda x: random.choice(x) if x else (EnumSales.NONE, [EnumDiscountEffect.NONE]))
            self.stock.loc[idx,"sale_type"] = self.stock.loc[idx,"sale_option"].apply(lambda x: x[0])
            self.stock.loc[idx,"discount_effect"] = self.stock.loc[idx,"sale_option"].apply(lambda x: random.choice(x[1]))
            
            mask = self.stock.index.isin(idx) & (self.stock["discount_effect"] == EnumDiscountEffect.BOGO) #split bogo and sales -> one to change servings one for pricing
            if len(self.stock[mask]) > 0:
                #self.stock.loc[mask,"servings"] = self.stock.loc[mask,"servings"] * self.stock.loc[mask,"discount_effect"].apply(lambda x: float(x.scaler))
                #self.stock.loc[mask,"price_per_serving"] = self.stock.loc[mask,"price_per_serving"]/self.stock.loc[mask,"discount_effect"].apply(lambda x: float(x.scaler) )
                #now the serving price is halved -> here div 2, cause the 2 is multiplied to servings (enum has only one scaler)
                result_rows = []
                if not isinstance(mask, int): #more than 1 row     

                    result_rows = [
                                processed_row
                                for _, row in self.stock.loc[mask].iterrows()
                                for processed_row in self.handle_bogo_per_row(row.copy(deep=True), row["discount_effect"].scaler)
                    ]
                    self.stock = self.stock[~mask]
                else: 
                    result_rows = self.handle_bogo_per_row(self.stock.iloc[mask].copy(deep=True), self.stock.loc[mask,"discount_effect"].scaler)  # type: ignore
                    self.stock = self.stock[~self.stock.index.isin([mask])]
                self.stock = pd.concat([self.stock, pd.DataFrame(result_rows)], ignore_index=True)
                self.stock = self.stock.reset_index(drop=True)
            mask = self.stock.index.isin(idx) & (self.stock["discount_effect"] != EnumDiscountEffect.BOGO)
            if len(self.stock[mask]) > 0:
                self.stock.loc[mask,"price_per_serving"] = self.stock.loc[mask,"price_per_serving"] * self.stock.loc[mask,"discount_effect"].apply(lambda x: float(x.scaler))
            
            self._update_deal_value()
            self.stock["sale_timer"] = self.stock["sale_type"].apply(lambda x: self.seasonal_duration if x == EnumSales.SEASONAL else globals.SALES_TIMER_PLACEHOLDER)
        
        self.stock = self.stock.drop(columns=["sale_option"])   
        
    def _update_deal_value(self) -> None: 
        #update deal value because servings size or price has changed
        a_1 =  globals.DEALASSESSOR_WEIGHT_SERVING_PRICE
        a_2 = 1- a_1
        self.stock["deal_value"] = a_1 * self.stock["price_per_serving"] + a_2 *\
                            self.stock["price_per_serving"] * self.stock["servings"]
        
 
    def _add_sales_options(self, item_mask: pd.Series, sale_option: list[tuple[EnumSales, list[EnumDiscountEffect]]]) -> None:
        #add item to the temporary list of possible sales to apply to the item 
        self.stock.loc[item_mask, 'sale_option'] = self.stock.loc[item_mask, 'sale_option'].apply(lambda x: x + sale_option)