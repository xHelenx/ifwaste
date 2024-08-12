from __future__ import annotations
import logging
import math
from os import replace
import random

from tempfile import tempdir
from typing import Callable, List, Optional
from numpy import add, take
import pandas as pd
from EnumSales import EnumSales
import globals
from FoodGroups import FoodGroups
from Store import Store 
class BasketCurator(): 
    
    def __init__(self,stores:list[Store],servings_to_buy_fg,budget:float) -> None:
        self.basket:pd.DataFrame = pd.DataFrame()
        self.stores:list[Store] = stores
        self.budget:float = budget
        self.likelihood_to_stop:float = float(globals.BASKETCURATOR_INITIAL_LIKELIHOOD)
        
        rows = []
        for fg in FoodGroups._instance.get_all_food_groups(): # type: ignore
                row = {'type': fg, 'required': servings_to_buy_fg[fg], 'got':0, 'is_in_other_fg': 0,
                        'is_replacing_other_fg': 0}
                rows.append(row)
        
        self.serv_track:pd.DataFrame = pd.DataFrame(rows)    
        self.serv_track = self.serv_track.astype(dtype={
            'type': 'str',
            'required': 'float',
            'got': 'float',
            'is_in_other_fg': 'float',
            'is_replacing_other_fg': 'float'
        }) 
        
         
    def _remove_item_without_replacement(self) -> bool: 
        if len(self.basket) > 0:
            item_to_replace = self.basket.sample(1,replace=True).iloc[0]
            self._remove_item(item_to_replace, item_to_replace["amount"])
            return True 
        else:
            return False
        
    def create_basket(self) -> None:
        '''
        servings_to_buy_fg = series FG:float
        '''
        logging.debug("###########################################")
        logging.debug("#####CREATE BASKET######")
        for store in self.stores: 
                logging.debug("--- STORES STOCK: ---")
                logging.debug(store.stock)
        #merge available stocks
        
        for fg in self.serv_track[self.serv_track["got"] < self.serv_track["required"]]["type"].tolist():
            options = self._get_product_options(self.stores, fgs=[fg], focus_on_sales=True)   
            if not options.empty: 
                options = options[options["amount"] > 0]                 
                row =  self.serv_track[self.serv_track["type"] == fg].iloc[0]
                needed_servings = row["required"]-row["got"]
                
                while needed_servings > 0: 
                    #TODO is ok that chooses fg from different stores?
                    if len(options) > 0:
                        plan_to_purchase = options.sample(1,replace=True).iloc[0]
                        self._buy(plan_to_purchase, 1)
                        options.loc[plan_to_purchase.name, "amount"] -= 1 # type: ignore #keep options current
                        options = options[options["amount"] > 0]
                        self._add_item(plan_to_purchase, 1)
                        needed_servings -= plan_to_purchase["servings"]
                    else:
                        break
            if len(self.basket) > 0: 
                self._organize_basket()
            #only if items have been bought we need to clean stock
            for store in self.stores: 
                store.clean_stock()    
        for store in self.stores: 
            logging.debug("--- STORES STOCK: ---")
            logging.debug(store.stock)
        if len(self.basket) > 0: 
            logging.debug("basket: #items:%i", self.basket["amount"].sum())
        else:
            logging.debug("basket: #items: 0")
        logging.debug(self.basket)    
                
    def is_basket_in_budget(self)-> bool: 
        '''
            returns True/False + budget
        
        '''
        if self.basket.empty:
            return True 
        cost = (self.basket["price_per_serving"] * self.basket["servings"]).sum()
        return cost < self.budget 
    
    def does_basket_cover_all_fg(self):
        return len(self.serv_track[self.serv_track["got"] < self.serv_track["required"]]) == 0 
    
    
    def adjust_basket(self) -> None:   
        if not self.does_basket_cover_all_fg():
            logging.debug("BASKET DOES NOT COVER ALL FG")
            self._add_items_from_another_fg()
            #now has_all_req_fg is still false, but we replaced it with other fgs
            
        #from now on we track if items have been adjusted
        self.basket["adjustment"] = "None"   
       
        if not self.is_basket_in_budget(): 
            logging.debug("BASKET IS NOT IN BUDGET")
            logging.debug("#####REPLACING: FIND CHEAPER OPTION; SAME FG######")
            self._apply_adjusting_strategy(self._replace_item_with_cheaper_option,False)
            (done,next_phase) = self._check_phase_status()
            while not done and not next_phase: 
                logging.debug("#####REPLACING: FIND CHEAPER OPTION; SAME FG######")
                self._apply_adjusting_strategy(self._replace_item_with_cheaper_option,False)
                (done,next_phase) = self._check_phase_status()
            if not done and next_phase: 
                logging.debug("#####REPLACING: FIND CHEAPER OPTION; ANY######")
                self._apply_adjusting_strategy(self._replace_item_with_cheaper_option,True)
                (done,next_phase) = self._check_phase_status()
                while not done and not next_phase: 
                    logging.debug("#####REPLACING: FIND CHEAPER OPTION; ANY######")
                    self._apply_adjusting_strategy(self._replace_item_with_cheaper_option,True)
                    (done,next_phase) = self._check_phase_status()
            if not done and next_phase: 
                logging.debug("#####REPLACING:DROP ITEMS ######")
                self._apply_adjusting_strategy(self._remove_item_without_replacement)
                (done,next_phase) = self._check_phase_status()
                while not done and not next_phase: 
                    logging.debug("#####REPLACING:DROP ITEMS ######")
                    self._apply_adjusting_strategy(self._remove_item_without_replacement)
                    (done,next_phase) = self._check_phase_status()       
    
        self.basket.drop(columns=["adjustment"])
    def _check_phase_status(self)-> tuple[bool,bool]:   
        #if done_ad true -> all true
             
        done_adjusting = False 
        #we are a) in budget, b) have an empty basket or c) tried to replace every items but it is the cheapest combo
        if self.is_basket_in_budget() or len(self.basket) == 0 or len(self.basket[self.basket["adjustment"] != "not_replaceable"]) == 0: 
            done_adjusting = True 
            next_phase = True 
        
        next_phase = False 
        #move to next state as there is no item that can be replaced
        if len(self.basket[self.basket["adjustment"] != "not_replaceable"]) == 0: 
            next_phase = True 
        
        #let the dice decide: 0-likeli = stop, likeli-(1-likli)/2=stay, (1-likli)/2-1 =next
        rand = random.uniform(0,1)
        if rand < self.likelihood_to_stop: 
            done_adjusting = True 
            next_phase = True 
        elif rand > self.likelihood_to_stop and \
            rand <= self.likelihood_to_stop + ((1-self.likelihood_to_stop)/2): 
            next_phase = False 
        else: #rand > self.likelihood_to_stop + ((1-self.likelihood_to_stop)/2): 
            next_phase = True
        
        return (done_adjusting, next_phase)
        
            
    def _apply_adjusting_strategy(self,func:Callable, *args) -> None: 
         
        found_cheaper_option = func(*args)
        in_budget = self.is_basket_in_budget()
        rand = random.uniform(0,1)
        self.likelihood_to_stop += globals.BASKETCURATOR_INCREMENT_LIKELIHOOD
        
        while not found_cheaper_option and not in_budget and rand > self.likelihood_to_stop: 
            found_cheaper_option = func(*args)
            in_budget = self.is_basket_in_budget()
            rand = random.uniform(0,1)
            self.likelihood_to_stop += globals.BASKETCURATOR_INCREMENT_LIKELIHOOD
            
                
    
    def _add_items_from_another_fg(self) -> None: 
        options = self._get_product_options(stores=self.stores, fgs=None, focus_on_sales=False)
    
        #sales and no sales here
        #buy items (can be larger serving size then needed)
        for _, row in self.serv_track.iterrows(): 
            
            while row["required"] > row["got"]:
                if not options.empty:
                    plan_to_purchase = options.sample(1,replace=True).iloc[0]
                    self._buy(plan_to_purchase, 1)
                    options.loc[plan_to_purchase.name, "amount"] -= 1 # type: ignore #keep options current
                    options = options[options["amount"] > 0]
                    self._add_item(plan_to_purchase, 1)
                else:
                    break

        
    def _update_serv_track(self, item:pd.Series, add_to_basket:bool) -> None: 
        
        if add_to_basket: 
            self._add_to_serv_track(item)
        else: 
            self._remove_from_serv_track(item)

    def _handle_is_replacing_other_fg(self, item: pd.Series, diff: int) -> float:
        #update servings in is_in_other_fg -> this is the fg that is replaced by another one
        
        self.serv_track.loc[self.serv_track["type"] == item["type"],"is_replacing_other_fg"] += diff # type: ignore
        assigned_servings = 0
        fgs_missing_servings = self.serv_track[self.serv_track['required'] > self.serv_track['got']]["type"].tolist()
        
        servings = diff
        while assigned_servings < diff and len(fgs_missing_servings) > 0:
            selected_fg = random.choice(fgs_missing_servings)
            
            max_servings = self.serv_track[self.serv_track["type"] == selected_fg]["required"].values[0] -\
                self.serv_track[self.serv_track["type"] == selected_fg]["got"].values[0]
            if servings > max_servings:
                servings = max_servings
            
            self.serv_track.loc[self.serv_track["type"] == selected_fg, "is_in_other_fg"] += servings # type: ignore
            self.serv_track.loc[self.serv_track["type"] == selected_fg, "got"] += servings # type: ignore
            
            assigned_servings += servings
            fgs_missing_servings = self.serv_track[self.serv_track['required'] > self.serv_track['got']]["type"].tolist()
            servings = diff - assigned_servings 
        return servings
        
    def _assign_remaining_servings(self, remaining_servings: float) -> None:
        random_row = self.serv_track.sample()
        self.serv_track.loc[random_row.index, "got"] += remaining_servings
        self.serv_track.loc[random_row.index, "is_replacing_other_fg"] += remaining_servings     


    def _add_to_serv_track(self,item:pd.Series) -> None: 
        #a) we are matching the food group we still need 
        fg_item = item["type"]
        servings = item["servings"]
        row = self.serv_track.loc[self.serv_track["type"] == fg_item]
        #update got value of item
        self.serv_track.loc[row.index[0],"got"] += item["servings"]
        
        #b) we are not matching, but we buy to meet serving requirements
        required = row["required"].values[0]
        got = self.serv_track.loc[row.index[0],"got"]
        is_replacing_other_fg = self.serv_track.loc[row.index[0],"is_replacing_other_fg"]
        
        if required < got:
            diff = got - (required + is_replacing_other_fg)
            #update servings in got + is_replacing_other_fg -> this is the replacing fg 
            remaining_servings = self._handle_is_replacing_other_fg(item, diff)
            
            if remaining_servings > 0:
                #randomly add it somewhere (even if it is technically not for another fg at this point)
                self._assign_remaining_servings(remaining_servings)

    def _remove_from_serv_track(self,item:pd.Series) -> None: 
        fg_item = item["type"]
        serv = item["servings"]
        row = self.serv_track.loc[self.serv_track["type"] == fg_item]
        
        self.serv_track.loc[row.index[0],"got"] -= serv
        
        is_replacing_other_fg = self.serv_track.loc[self.serv_track["type"]==item["type"], "is_replacing_other_fg"].iloc[0] # type: ignore
        is_in_other_fg = self.serv_track.loc[self.serv_track["type"]==item["type"], "is_in_other_fg"].iloc[0] # type: ignore
        got = self.serv_track.loc[row.index[0],"got"]
        
        servings_to_remove = serv
        
        if is_replacing_other_fg + is_in_other_fg > got: # type: ignore 
            #first start with replacing_other_fg (easier)
            servings_to_remove = is_replacing_other_fg + is_in_other_fg - got 
            replace_amount = servings_to_remove
            if is_replacing_other_fg > 0: 
                if is_replacing_other_fg < replace_amount:
                    replace_amount = is_replacing_other_fg
                self.serv_track.loc[row.index[0],"is_replacing_other_fg"] -= replace_amount
                servings_to_remove -= replace_amount
            if servings_to_remove > 0: 
                #now replace it from is_in_other_fg 
                replace_amount = servings_to_remove
                self.serv_track.loc[row.index[0],"is_in_other_fg"] -= replace_amount
                #and now from other fgs too
            
                while  servings_to_remove > 0:  # type: ignore
                    replace_amount = servings_to_remove
                    item = self.serv_track[self.serv_track["is_replacing_other_fg"] > 0].sample(1,replace=True).iloc[0]
                    if replace_amount > item["is_replacing_other_fg"]:
                        replace_amount = item["is_replacing_other_fg"]
                    
                    self.serv_track.loc[self.serv_track["type"] == item["type"], "got"] -= replace_amount # type: ignore
                    self.serv_track.loc[self.serv_track["type"] == item["type"], "is_replacing_other_fg"] -= replace_amount # type: ignore
                    servings_to_remove -= replace_amount # type: ignore
                
            
    def _replace_item_with_cheaper_option(self, is_same_fg:bool=False) -> bool:
        
        found_replaceable_item = False #might have to try every item in self.basket
        options = self._get_product_options(self.stores,None,focus_on_sales=False)
        options["adjustment"] = "None" 
        
        #adjustment options:         
        #not_replaceable - was attempted to be replaced for a different item, but there was no better option
        #replacement_failed - temporily indicates that item was not able to replace "item_to_replace"
        #None - has not been used yet
        
        while not found_replaceable_item:
            #choose item to replace, that has not been attempted to be replaced
            if len(self.basket[self.basket["adjustment"] != "not_replaceable"]) == 0: 
                break 
            item_to_replace = self.basket[self.basket["adjustment"] == "None"].sample(1,replace=True).iloc[0]
            mask =  (options["price_per_serving"] < item_to_replace["price_per_serving"])
            if is_same_fg: 
                mask = mask & (options["type"] == item_to_replace["type"]) 
            replace_with = options[mask]
            replace_with.loc[replace_with["adjustment"] == "replacement_failed","adjustment"] = None #new item to check, so reset  
            if len(replace_with) > 0: #replacable items exist                
                is_replaced = False #try each possible replacement for chosen item to replace
                req_servings = item_to_replace["servings"] * item_to_replace["amount"] 
                max_price =  item_to_replace["servings"] * item_to_replace["price_per_serving"] * item_to_replace["amount"] 
                rep_servings = 0
                rep_amount = 0
                while not is_replaced and not len(replace_with) == 0:
                    (has_sufficient_serv,req_servings, replacement, rep_amount) = self._get_amount_to_replace(replace_with, req_servings-rep_servings)
                    cost = replacement["servings"] * replacement["price_per_serving"] * rep_amount   
                    if cost < max_price and has_sufficient_serv :  #sufficient servings + cheaper through 1 product
                        self._handle_item_exchange(                  
                                give_back=[item_to_replace], 
                                take_instead=[replacement], 
                                amount_give_back=[item_to_replace["amount"]],
                                amount_take_instead=[rep_amount])
                        is_replaced = True 
                        found_replaceable_item = True
                        logging.debug("ITEM TO REPLACE, Q:%i", item_to_replace["amount"])
                        logging.debug(item_to_replace.tolist())
                    
                        logging.debug("REPLACEMENT, Q:%i", rep_amount)
                        logging.debug(replacement.tolist())
                    elif cost < max_price and not has_sufficient_serv: #insufficient servings but cheaper -> find 1 more item type to fill gap
                        if len(replace_with) > 1: #at least 2 items 
                            idx = self.get_idx_of_identical_item_df(replacement, replace_with)
                            tmp_replace_with = replace_with.drop(idx) #remove already considered option from options 
                            (has_sufficient_serv,req_servings, replacement2, rep_amount2) = self._get_amount_to_replace(tmp_replace_with, req_servings-0)
                            cost += replacement2["servings"]* replacement2["price_per_serving"]* rep_amount2 #add cost of 2nd item
                            if cost < max_price and has_sufficient_serv: 
                                self._handle_item_exchange(              
                                    give_back=[item_to_replace], 
                                    take_instead=[replacement, replacement2], 
                                    amount_give_back=[item_to_replace["amount"]],
                                    amount_take_instead=[rep_amount, rep_amount2])
                                is_replaced = True 
                                found_replaceable_item = True
                                logging.debug("ITEM TO REPLACE, Q:%i", item_to_replace["amount"])
                                logging.debug(item_to_replace.tolist())
                            
                                logging.debug("REPLACEMENT, Q1:%i, Q2:%i", rep_amount, rep_amount2)
                                logging.debug(replacement.tolist())
                                logging.debug(replacement2.tolist())
                            else: #could repress optimal solution, but we dont want optimal solution
                                self._set_replacement_status(replacement, replace_with, "replacement_failed")
                                self._set_replacement_status(replacement2, replace_with, "replacement_failed")
                        else: #could repress optimal solution, but we dont want optimal solution
                            self._set_replacement_status(replacement, replace_with, "replacement_failed")
                    elif cost >= max_price: #replacement item is no valid candidate
                        self._set_replacement_status(replacement, replace_with, "replacement_failed")
                    replace_with = replace_with[replace_with["adjustment"] != "replacement_failed"] #filter failed attempts out
                if not is_replaced and len(replace_with) == 0: 
                    self._set_replacement_status(item_to_replace, self.basket, "not_replaceable") # type: ignore
            else: 
                self._set_replacement_status(item_to_replace, self.basket, "not_replaceable") # type: ignore
            
        logging.debug("BASKET AFTER REPLACEMENT")
        logging.debug(self.basket)
        return found_replaceable_item
    def _set_replacement_status(self, item:pd.Series, df:pd.DataFrame, status:str) -> None: 
        idx = self.get_idx_of_identical_item_df(item,df=df) # type: ignore
        assert idx != None 
        df.loc[idx, "adjustment"] = status
        
    def _handle_item_exchange(self,give_back: Optional[List] = None, take_instead: Optional[List] = None,
                              amount_give_back: Optional[List[int]] = None, amount_take_instead: Optional[List[int]] = None ) -> None:
        # update basket changes
        if give_back != None and amount_give_back != None: 
            for i in range(len(give_back)): 
                self._give_back(item=give_back[i], amount=amount_give_back[i]) #to store
                self._remove_item(give_back[i], amount_give_back[i]) #from basket
        
        if take_instead != None and amount_take_instead != None :    
            for i in range(len(take_instead)): 
                self._buy(item=take_instead[i], amount=amount_take_instead[i])
                self._add_item(take_instead[i], amount_take_instead[i])
        
    def _add_item(self, item:pd.Series, amount:int) -> None:
        item["amount"] = amount
        self._update_serv_track(item=item,add_to_basket=True)    
        self.basket = pd.concat([self.basket, pd.DataFrame([item])], ignore_index=True)
        self._organize_basket()
       
    def _organize_basket(self) -> None: 
        equal_columns = self.basket.columns.tolist()
        equal_columns.remove("amount") 
        self.basket = self.basket.groupby(equal_columns, as_index=False)['amount'].sum()         # type: ignore
        
    def _remove_item(self, item:pd.Series, amount:int) -> None: 
        idx = self.get_idx_of_identical_item_df(item,self.basket)
        assert idx != None 
        amount_in_basket = self.basket.loc[idx, "amount"]
        
        if amount_in_basket == amount: 
            self.basket = self.basket.drop(idx)
            item["amount"]  = amount
            self._update_serv_track(item=item, add_to_basket=False)
        elif amount_in_basket > amount:  # type: ignore
            self.basket.loc[idx, "amount"] -= amount # type: ignore
            item["amount"]  = amount
            self._update_serv_track(item=item, add_to_basket=False)
        else: 
            raise ValueError("Error attempting to remove more items from basket than basket contains")
        
        self._organize_basket()
    
    def _get_amount_to_replace(self, replace_options, req_servings) -> tuple[bool,float,pd.Series,int]: 
        #sample a possible option
        assert replace_options is not None 
    
        replacement = replace_options.sample(1,replace=True).iloc[0]
        rep_amount = 0
        rep_servings = 0
        #figure out how many items to buy from this type 
        while (req_servings > rep_servings) and (rep_amount + 1 < replacement["amount"]): 
            rep_servings += replacement["servings"]
            rep_amount += 1 
    
                    
        missing_servings = rep_servings - req_servings
        has_enough = missing_servings >= 0 
        if missing_servings < 0: 
            missing_servings = 0
        return (has_enough,missing_servings, replacement, rep_amount)
        
    
    def _buy(self,item:pd.Series,amount:int) -> None:
        """Buy item in amount from store

        Args:
            item (pd.Series): Item to be bought
            amount (int): amount of items to be bought of the items characteristic

        Returns:
            float: returns cost of the purchase (- n -> gain n, +n -> pay n)
        """        
        store = item["store"] #take replacement from store
        store.buy(item, amount)
        
    def _give_back(self,item:pd.Series,amount:int) -> None:
        """Return item in amount from store

        Args:
            item (pd.Series): Item to be returned
            amount (int): amount of items to be returned of the items characteristic

        Returns:
            float: returns cost of the purchase (- n -> gain n, +n -> pay n)
        """          
        store = item["store"] #give item back to store
        store.give_back(item, amount)
        
    
    def _get_product_options(self, stores, fgs=None, focus_on_sales=False) -> pd.DataFrame: 
        """_summary_

        Args:
            stores (_type_): _description_
            fgs (_type_, optional): _description_. Defaults to None.
            focus_on_sales (bool, optional): _description_. Defaults to False.
            cheaper_than (float, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        
        options = pd.DataFrame()
        #go over required food groups
        if fgs == None: 
            for store in stores: 
                if len(options) == 0:
                    options = store.stock
                else: 
                    options = pd.concat([options,store.stock], ignore_index=True)    
        else: 
            for fg in fgs:
                for store in stores: 
                    if store.is_fg_in_stock(fg): 
                        if len(options) == 0: 
                            options = store.get_stock_of_fg(fg)
                        else: 
                            options = pd.concat([options,store.get_stock_of_fg(fg)], ignore_index=True)
        if len(options) > 0 and focus_on_sales : 
            items_on_sale = options[options["sale_type"] != EnumSales.NONE] 
            if len(items_on_sale) > 0: 
                #if items are on sale buy from those (even tho might not be best deal)
                options = items_on_sale     
                
        
        return options 
    
    def return_basket_to_store(self) -> None: 
        for _,row in self.basket.iterrows(): 
            self._remove_item(item=row, amount=row["amount"])
            
    
    def get_missing_fgs(self) -> list[str]:
        return self.serv_track[self.serv_track["got"] >= self.serv_track["required"]]["type"].tolist()
    
    def get_visited_stores(self):
        if len(self.basket) > 0:
            return self.basket["store"].unique().tolist()
        
    
    def get_idx_of_identical_item_df(self,item:pd.Series, df:pd.DataFrame) -> None | int :
        """Takes a stock item and returns stock item with the same characteristics
        (besides amount). Helper function to manipulate stock items. 

        Args:
            item (pd.Dataframe): _description_

        Returns:
            pd.Dataframe: selected row that matches the item attributes, if none matches
            returns None 
        """        
        # Find the index of the matching row
        idx = df.loc[
            (df["type"] == item["type"]) &
            (df["servings"] == item["servings"]) &
            (df["days_till_expiry"] == item["days_till_expiry"]) &
            (df["sale_type"] == item["sale_type"]) &
            (df["store"] == item["store"])
        ].index

        # If you expect only one match, you can get the first index
        if not idx.empty:
            return idx[0]