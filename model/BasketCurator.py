from __future__ import annotations
import logging
import random

from typing import Callable, List, Optional
import pandas as pd
from EnumSales import EnumSales
import globals
from FoodGroups import FoodGroups
from Store import Store
from EnumDiscountEffect import EnumDiscountEffect 

class BasketCurator(): 
    
    def __init__(self,stores:list[Store],servings_to_buy_fg:pd.Series | None=None,budget:float | None = None, logger:logging.Logger|None=None) -> None:
        """initalizes BasketCurator.

        Args:
            stores (list[Store]): _description_
            servings_to_buy_fg (pd.Series | None, optional): _description_. Defaults to None.
            budget (float | None, optional): _description_. Defaults to None.
            
         Class variables: 
            basket (pd.DataFrame) : selected items to buy
            stores (list[Stores]) : selected store options to buy from 
            budget (float)        : budget for this shopping tour 
            likelihood_to_stop (float) : chance of stopping to adjust basket and purchasing the 
                                         current basket composition 
            serv_track (pd.DataFrame) : helping df to keep track of bought and needed servings                                        
            
        """      
        self.logger: logging.Logger|None = logger  
        self.basket:pd.DataFrame = pd.DataFrame()
        self.stores:list[Store] = stores
        self.budget:float | None = budget
        self.likelihood_to_stop:float = 0
        
        rows = []
        if servings_to_buy_fg is None:
            servings_to_buy_fg = pd.Series()
            for fg in FoodGroups._instance.get_all_food_groups(): # type: ignore 
                servings_to_buy_fg[fg] = 0 
            
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
        """Removes a random item item from the basket

        Returns:
            bool: An item has been replaced
        """        
        if len(self.basket) > 0:
            item_to_replace = self.basket.sample(1,replace=True).iloc[0]
            self._remove_item(item_to_replace, item_to_replace["amount"])
            return True 
        else:
            return False
        
    def create_basket(self, is_quickshop:bool=False) -> None:
        """Creates a shopping basket 
        Args:
            is_quickshop (bool, optional): Toggles between quickshop and shopping. Defaults to False.
        """        
        #new day so reset: self.likelihood_to_stop
        self.likelihood_to_stop = 0       
        
        globals.log(self,"#####CREATE BASKET######")
       
        if not is_quickshop:
            self._create_shop_basket()
        else:
            self._create_quickshop_basket()
                       
        if len(self.basket) > 0: 
            self._organize_basket()        
            globals.log(self,"is_quickshop: %s, basket: #items:%i, cost %f",is_quickshop, self.basket["amount"].sum(), (self.basket["price_per_serving"] * self.basket["servings"]).sum())
        else:
            globals.log(self,"is_quickshop: %s basket: #items: 0", is_quickshop)
        globals.log(self,self.basket)    
      
    def _get_purchased_servings_from_serv_track(self) -> pd.Series: 
        """Helper function, that returns how many servings of each food type have already been 
        selected

        Returns:
            pd.Series: Series including the purchased items per food group
        """        
        return self.serv_track["got"] + self.serv_track["is_in_other_fg"] - self.serv_track["is_replacing_other_fg"]
    
    def _sample_and_buy(self,options:pd.DataFrame) -> pd.Series: 
        """Samples a single item to buy from the options and manages
        the purchase process from the store + move the item to the basket 
        and updates the serving tracker

        Args:
            options (pd.DataFrame): Options that can be bought

        Returns:
            pd.Series: chosen item 
        """        
        # buy 1 
        plan_to_purchase = options.sample(1,replace=True).iloc[0]
        self._buy(plan_to_purchase, 1)
        options.loc[plan_to_purchase.name, "amount"] -= 1 # type: ignore #keep options current
        options = options[options["amount"] > 0]
        self._add_item(plan_to_purchase, 1)
    
        return plan_to_purchase  
    
    
    def _create_shop_basket(self) -> None: 
        """Creates a shopping basket (not quickshop) based on self.stores as store options and
        self.budget.
        """        
        #merge available stocks
        for fg in self.serv_track[self._get_purchased_servings_from_serv_track()  < self.serv_track["required"]]["type"].tolist():
            options = self._get_stock_options(fgs=[fg], focus_on_sales=True)   
            if not options.empty: 
                options = options[options["amount"] > 0]                 
                idx =  self.serv_track[self.serv_track["type"] == fg].index[0]
                needed_servings = self.serv_track.loc[idx,"required"]- self._get_purchased_servings_from_serv_track().loc[idx]
                
                while needed_servings > 0: 
                    options = options[options["amount"] > 0]    ####new
                    options = options.dropna()
                    if len(options) > 0:
                        purchased = self._sample_and_buy(options)
                        needed_servings -= purchased["servings"]
                    else:
                        break
    def impulse_buy(self,  impulsivity:float): 
        ##adds random item to basket
        
        ##determine amount of items bought
        ##n% of that can be bought max, check each time
        n_items:int = int(len(self.basket) * globals.HH_IMPULSE_BUY_PERCENTAGE)
        #get options from all possible stores
        options = self._get_stock_options()
        options = self._add_impulse_buy_likelihood_column(options)
        #add likelihood columns
        for _ in range(n_items): 
            if random.random() < impulsivity: 
                #buy random item
                item = options.sample(1, weights='impulse_buy_likelihood').iloc[0]
                self._buy(item, 1)
                options.loc[item.name, "amount"] -= 1 # type: ignore #keep options current
                options = options[options["amount"] > 0]
                self._add_item(item, 1)
                
    def _add_impulse_buy_likelihood_column(self,options): 
        # Convert food_groups to a DataFrame for merging
        food_groups_df = pd.DataFrame(FoodGroups._instance.food_groups) # type: ignore
        
        # Merge the options with food_groups_df to add the impulse_buy_likelihood
        options = options.merge(food_groups_df[['type', 'impulse_buy_likelihood']], on='type', how='left')
        
        # Fill any missing likelihoods with 0 (or a minimum value) if needed
        options['impulse_buy_likelihood'] = options['impulse_buy_likelihood'].fillna(0)
        
        # Normalize the likelihoods to get probabilities
        total_likelihood = options['impulse_buy_likelihood'].sum()
        options['impulse_buy_likelihood'] = options['impulse_buy_likelihood'] / total_likelihood
        
        return options
        
        
                    
    def _create_quickshop_basket(self) -> None: 
        """Creates a shopping basket (quickshop) based on self.stores as store options and
        self.budget.
        
        In this case only a single store can be visited. If available if it will one item 
        of the FGSTOREPREPARED food group and 1-n random other food items.
        
        """ 
        #only allow 1 store to be visited! 
        
        options = self._get_stock_options(fgs=[globals.FGSTOREPREPARED]) 
        options = options.dropna()
        if not options.empty:
            self._sample_and_buy(options)
        
        options = self._get_stock_options()
        n = random.randint(1,globals.BASKETCURATOR_MAX_ITEMS_QUICKSHOP)
        
        for _ in range(n): 
            options = options[options["amount"] > 0]
            options = options.dropna()
            if options.empty: 
                break
            self._sample_and_buy(options)
        
    def is_basket_in_budget(self)-> bool: 
        '''
        Returns whether the current curate basket meets the defined budget.
        
        Returns: bool: basket is in budget        
        '''
        if self.basket.empty:
            return True 
        cost = (self.basket["price_per_serving"] * self.basket["servings"]).sum()
        return cost < self.budget 
    
    def does_basket_cover_all_fg(self) -> bool:
        """Returns whether the basekt covers servings of all food groups that were planned 
        to be purchased. 

        Returns:
            bool: basket covers servings of all required food groups
        """        
        return len(self.serv_track[self.serv_track["got"] + self.serv_track["is_in_other_fg"] < self.serv_track["required"]]) == 0 
    
    
    def adjust_basket(self) -> None:   
        """Method to adjust the basket, if it is not in budget or it does not cover 
        the servings of the required food groups. 3 strategies will over time be applied 
        including (1. replace items with cheaper items of same food group, 2. replace items 
        with a cheaper item of any food group, 3. remove item without replacement). 
        There is a increasing likelihood for the adjusting process to be interrupted early as well
        as an increasing likelihood to move on to a more strict replacement strategy.
        
        Important: Intentionally does not guarantee, that the basket is in budget and does cover all food groups 
        as initially defined
        """        
        
       # for store in self.stores:
       #     store.organize_stock()      
        self._organize_basket()
        
        
        if not self.does_basket_cover_all_fg():
            globals.log(self,"BASKET DOES NOT COVER ALL FG")
            self._add_items_from_another_fg()
            #now has_all_req_fg is still false, but we replaced it with other fgs
        
        if not self.is_basket_in_budget(): 
            #from now on we track if items have been adjusted
            self.basket["adjustment"] = "None"   
       
            globals.log(self,"BASKET IS NOT IN BUDGET")
            globals.log(self,"#####REPLACING: FIND CHEAPER OPTION; SAME FG######")
            self._apply_adjusting_strategy(self._replace_item_with_cheaper_option,False)
            (done,next_phase) = self._check_phase_status()
            while not done and not next_phase: 
                globals.log(self,"#####REPLACING: FIND CHEAPER OPTION; SAME FG######")
                self._apply_adjusting_strategy(self._replace_item_with_cheaper_option,False)
                (done,next_phase) = self._check_phase_status()
            if not done and next_phase: 
                globals.log(self,"#####REPLACING: FIND CHEAPER OPTION; ANY######")
                self._apply_adjusting_strategy(self._replace_item_with_cheaper_option,True)
                (done,next_phase) = self._check_phase_status()
                while not done and not next_phase: 
                    globals.log(self,"#####REPLACING: FIND CHEAPER OPTION; ANY######")
                    self._apply_adjusting_strategy(self._replace_item_with_cheaper_option,True)
                    (done,next_phase) = self._check_phase_status()
            if not done and next_phase: 
                globals.log(self,"#####REPLACING:DROP ITEMS ######")
                self._apply_adjusting_strategy(self._remove_item_without_replacement)
                (done,next_phase) = self._check_phase_status()
                while not done and not next_phase: 
                    globals.log(self,"#####REPLACING:DROP ITEMS ######")
                    self._apply_adjusting_strategy(self._remove_item_without_replacement)
                    (done,next_phase) = self._check_phase_status()       
            if "adjustment" in self.basket.columns: 
                self.basket.drop(columns=["adjustment"])
    def _check_phase_status(self)-> tuple[bool,bool]:   
        """Handles the logic of changing the adjustment strategy as well as 
        the early stop of attempting to change the basket. 

        Returns:
            tuple[bool,bool]: The first value indicates whether the whole adjustment is done, 
            the second indicates, whether to move on to the next replacement strategy
        """
                     
        done_adjusting = False 
        #we are a) in budget, b) have an empty basket or c) tried to replace every items but it is the cheapest combo
        if (self.is_basket_in_budget() or len(self.basket) == 0 or \
            ("adjustment" in self.basket.columns and len(self.basket[self.basket["adjustment"] != "not_replaceable"]) == 0)):
            done_adjusting = True 
            next_phase = True 
        
        next_phase = False 
        #move to next state as there is no item that can be replaced
        if "adjustment" in self.basket.columns and len(self.basket[self.basket["adjustment"] != "not_replaceable"]) == 0: 
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
        """Receives a function and its parameters and applies the adjusting method to the 
        basket until either the basket does now match the budget or an early stop/move on occurs.

        Args:
            func (Callable): a function [_replace_item_with_cheaper_option, _remove_item_without_replacement]
            *args          : for _replace_item_with_cheaper_option either True or False, does not have to be 
                            added for _remove_item_without_replacement 

        """        
         
        found_cheaper_option = func(*args)
        in_budget = self.is_basket_in_budget()
        rand = random.uniform(0,1)
        self.likelihood_to_stop += globals.BASKETCURATOR_INCREMENT_LIKELIHOOD
        
        while not found_cheaper_option and not in_budget and rand > self.likelihood_to_stop: 
            found_cheaper_option = func(*args)
            in_budget = self.is_basket_in_budget()
            rand = random.uniform(0,1)
            self.likelihood_to_stop += globals.BASKETCURATOR_INCREMENT_LIKELIHOOD
        self._organize_basket()    
             
    
    def _add_items_from_another_fg(self) -> None: 
        """
        Buys items from another food group until the the missing servings (required <= purchased servings)
        have been compensated.
        """        
        options = self._get_stock_options(fgs=None, focus_on_sales=False)
        options = options.dropna()
    
        #sales and no sales here
        #buy items (can be larger serving size then needed)
        for idx in self.serv_track.index: 
            
            while self.serv_track.loc[idx, "required"] > self._get_purchased_servings_from_serv_track().loc[idx]:
                if not options.empty:
                    self._sample_and_buy(options)
                else:
                    break
        self._organize_basket()
        
    def _update_serv_track(self, item:pd.Series, add_to_basket:bool) -> None: 
        """Manages the serving tracker, will add and remove items from the tracking system

        Args:
            item (pd.Series): item to be added or removed
            add_to_basket (bool): true for added, false for removed
        """        
        
        if add_to_basket: 
            self._add_to_serv_track(item)
        else: 
            self._remove_from_serv_track(item)

    def _handle_is_replacing_other_fg(self, item: pd.Series, diff: int) -> float:
        """Helper function to update the serv_tracker, when an item is replacing an item of
        another fg

        Args:
            item (pd.Series): item that is replacing another item
            diff (int): servings to assign in another fg

        Returns:
            float: _description_
        """        
        #update servings in is_in_other_fg -> this is the fg that is replaced by another one
        
        self.serv_track.loc[self.serv_track["type"] == item["type"],"is_replacing_other_fg"] += diff # type: ignore
        assigned_servings = 0
        fgs_missing_servings = self.serv_track[self.serv_track['required'] > self._get_purchased_servings_from_serv_track()]["type"].tolist()
        
        servings = diff
        while assigned_servings < diff and len(fgs_missing_servings) > 0:
            selected_fg = random.choice(fgs_missing_servings)
            
            max_servings = self.serv_track[self.serv_track["type"] == selected_fg]["required"].values[0] -\
                self._get_purchased_servings_from_serv_track().loc[self.serv_track["type"] == selected_fg].values[0]
            if servings > max_servings:
                servings = max_servings
            
            self.serv_track.loc[self.serv_track["type"] == selected_fg, "is_in_other_fg"] += servings # type: ignore
           # self.serv_track.loc[self.serv_track["type"] == selected_fg, "got"] += servings # type: ignore
            
            assigned_servings += servings
            fgs_missing_servings = self.serv_track[self.serv_track['required'] > self._get_purchased_servings_from_serv_track()]["type"].tolist()
            servings = diff - assigned_servings 
        return servings
        
    def _assign_remaining_servings(self, remaining_servings: float) -> None:
        """Helper function for serv tracker that manages the assignment of remaining
        servings.

        Args:
            remaining_servings (float): amount of remaining servings
        """        
        random_row = self.serv_track.sample()
        self.serv_track.loc[random_row.index, "got"] += remaining_servings
        self.serv_track.loc[random_row.index, "is_replacing_other_fg"] += remaining_servings     


    def _add_to_serv_track(self,item:pd.Series) -> None: 
        """Manage the addition of an item to the serv tracker

        Args:
            item (pd.Series): item to add
        """        
        #a) we are matching the food group we still need 
        fg_item = item["type"]
        row = self.serv_track.loc[self.serv_track["type"] == fg_item]
        #update got value of item
        self.serv_track.loc[row.index[0],"got"] += item["servings"]
        
        #b) we are not matching, but we buy to meet serving requirements
        required = row["required"].values[0]
        got = self._get_purchased_servings_from_serv_track()
        if row["required"].values[0] < got.loc[row.index[0]] :
            diff = got.loc[row.index[0]] - required
            #update servings in got + is_replacing_other_fg -> this is the replacing fg 
            remaining_servings = self._handle_is_replacing_other_fg(item, diff)
            
            if remaining_servings > 0:
                #randomly add it somewhere (even if it is technically not for another fg at this point)
                self._assign_remaining_servings(remaining_servings)

    def _remove_from_serv_track(self,item:pd.Series) -> None: 
        """Manages the removal of an item from the serv tracker

        Args:
            item (pd.Series): item to remove
        """        
        fg_item = item["type"]
        serv = item["servings"]
        row = self.serv_track.loc[self.serv_track["type"] == fg_item]
        
        self.serv_track.loc[row.index[0],"got"] -= serv
        
        is_replacing_other_fg = self.serv_track.loc[self.serv_track["type"]==item["type"], "is_replacing_other_fg"].iloc[0] # type: ignore
        is_in_other_fg = self.serv_track.loc[self.serv_track["type"]==item["type"], "is_in_other_fg"].iloc[0] # type: ignore
        got = self.serv_track.loc[row.index[0],"got"]
        
        servings_to_remove = serv
        
        if is_replacing_other_fg > got: # type: ignore 
            #first start with replacing_other_fg (easier)
            servings_to_remove = is_replacing_other_fg - got 
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
                    
                    #self.serv_track.loc[self.serv_track["type"] == item["type"], "got"] -= replace_amount # type: ignore
                    self.serv_track.loc[self.serv_track["type"] == item["type"], "is_replacing_other_fg"] -= replace_amount # type: ignore
                    servings_to_remove -= replace_amount # type: ignore
                
            
    def _replace_item_with_cheaper_option(self, is_same_fg:bool=False) -> bool:
        """Performs the adjustment method to replace as single item with a cheaper optoin

        Args:
            is_same_fg (bool, optional): Toggles whether the replacement item has to
            be of the same food groups (true) or any food group. Defaults to False.

        Returns:
            bool: was an replacement found
        """        
        
        found_replaceable_item = False #might have to try every item in self.basket
        options = self._get_stock_options(None,focus_on_sales=False)
        options["adjustment"] = "None" 
        self.basket["adjustment"] = "None"
        
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
                        globals.log(self,"ITEM TO REPLACE, Q:%i", item_to_replace["amount"])
                        globals.log(self,item_to_replace.tolist())
                    
                        globals.log(self,"REPLACEMENT, Q:%i", rep_amount)
                        globals.log(self,replacement.tolist())
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
                                globals.log(self,"ITEM TO REPLACE, Q:%i", item_to_replace["amount"])
                                globals.log(self,item_to_replace.tolist())
                            
                                globals.log(self,"REPLACEMENT, Q1:%i, Q2:%i", rep_amount, rep_amount2)
                                globals.log(self,replacement.tolist())
                                globals.log(self,replacement2.tolist())
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
            
        return found_replaceable_item
    def _set_replacement_status(self, item:pd.Series, df:pd.DataFrame, status:str) -> None: 
        """Helper function that updates whether 
            - an option cannot replace the item (e.g. its more expensive): replacement_failed
            - the item itself could not be replaced by any item: not_replaceable

        Args:
            item (pd.Series): item to replace
            df (pd.DataFrame): options
            status (str): ["replacement_failed", "not_replaceable"]
        """        
        idx = self.get_idx_of_identical_item_df(item,df=df) # type: ignore
        assert idx != None 
        df.loc[idx, "adjustment"] = status
        
    def _handle_item_exchange(self,give_back: Optional[List] = None, take_instead: Optional[List] = None,
                              amount_give_back: Optional[List[int]] = None, amount_take_instead: Optional[List[int]] = None ) -> None:
        """Handles the replacement of on item (give_back) for another (take_instead). Handles 
        the return/purchase from a store and removes/add the item to the basket and tracker

        Args:
            give_back (Optional[List], optional): List of items to give back. Defaults to None.
            take_instead (Optional[List], optional): List of items to buy instead. Defaults to None.
            amount_give_back (Optional[List[int]], optional): how many items to give back of each type. Defaults to None.
            amount_take_instead (Optional[List[int]], optional): how many items to take instead of each type. Defaults to None.
        """        
        if give_back != None and amount_give_back != None: 
            for i in range(len(give_back)): 
                self._give_back(item=give_back[i], amount=amount_give_back[i]) #to store
                self._remove_item(give_back[i], amount_give_back[i]) #from basket
        
        if take_instead != None and amount_take_instead != None :    
            for i in range(len(take_instead)): 
                self._buy(item=take_instead[i], amount=amount_take_instead[i])
                self._add_item(take_instead[i], amount_take_instead[i])
        
    def _add_item(self, item:pd.Series, amount:int) -> None:
        """Adds item to basket

        Args:
            item (pd.Series): item to add
            amount (int): amount of instance to add
        """        
        item["amount"] = amount
        self._update_serv_track(item=item,add_to_basket=True)    
        self.basket = pd.concat([self.basket, pd.DataFrame([item])], ignore_index=True)
       
    def _organize_basket(self) -> None: 
        """Organizes the basket, by merging identical items into one row and the the 
        summed amount
        
        """        

        if len(self.basket) > 0: 
            # Temporarily convert enums to string for grouping
            self.basket['discount_effect'] = self.basket['discount_effect'].astype(str)
            self.basket['sale_type'] = self.basket['sale_type'].astype(str)

            equal_columns = ["type", "servings", "days_till_expiry", "price_per_serving", "store", "sale_type", "discount_effect", "deal_value", 
                            "sale_timer", "ID"]
            self.basket = self.basket.groupby(equal_columns, as_index=False)['amount'].sum() # type: ignore

            # Convert str of enums back to enums
            self.basket['sale_type'] = self.basket['sale_type'].apply(lambda x: globals.to_EnumSales(x))   # type: ignore
            self.basket['discount_effect'] = self.basket['discount_effect'].apply(lambda x: globals.to_EnumDiscountEffect(x))  # type: ignore # Adjust to your enum class if different

        
    def _remove_item(self, item:pd.Series, amount:int) -> None: 
        """Removes item from the basket

        Args:
            item (pd.Series): item to remove
            amount (int): amount of instance to remove

        Raises:
            ValueError: Avoid removing more items from the basket than there are 
            in the basket
        """        
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
    
    def _get_amount_to_replace(self, replace_options:pd.DataFrame, req_servings:float) -> tuple[bool,float,pd.Series,int]: 
        """Samples a replacement options (not bought yet, just preselected) and calculates how many items would be necessary of it 
        to replace the original items

        Args:
            replace_options (pd.DataFrame): _description_
            req_servings (float): _description_

        Returns:
            tuple[bool,float,pd.Series,int]: (has_enough,missing_servings, replacement, rep_amount)
            1. bool: would the chosen item (+ amount) be enough to cover the missing servings
            2. float: how many servings are missing after adding this item 
            3. pd.Series: item chosen for being the replacement
            4. int: amount of replacement item
        """        
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
        store.organize_stock(item) 
        
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
        
    
    def _get_stock_options(self, fgs:List[str] | None =None, focus_on_sales:bool=False) -> pd.DataFrame: 
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
            for store in self.stores: 
                if len(options) == 0:
                    options = store.stock.copy(deep=True)
                else: 
                    options = pd.concat([options, store.stock.copy(deep=True)], ignore_index=True)
        else: 
            for fg in fgs:
                for store in self.stores: 
                    if store.is_fg_in_stock(fg): 
                        if len(options) == 0: 
                            options = store.get_stock_of_fg(fg)
                        else: 
                            options = pd.concat([options, store.stock.copy(deep=True)], ignore_index=True)
        if len(options) > 0 and focus_on_sales : 
            items_on_sale = options[options["sale_type"] != EnumSales.NONE] 
            if len(items_on_sale) > 0: 
                #if items are on sale buy from those (even tho might not be best deal)
                options = items_on_sale
        return options 
    
    def return_basket_to_store(self) -> None: 
        """Returns the entire basket to the store(s)
        """        
        for _,row in self.basket.iterrows(): 
            self._remove_item(item=row, amount=row["amount"])
            self._give_back(item=row,amount=row["amount"])
            
    
    def get_missing_fgs(self) -> list[str]:
        """Returns which food groups are not sufficiently in the basket yet (missing servings)

        Returns:
            list[str]: Returns a list of string representation of the food groups
        """        
        return self.serv_track[self.serv_track["got"] >= self.serv_track["required"]]["type"].tolist()
    
    def get_visited_stores(self) -> list[Store] | None:
        """Returns the stores visited based on the items in the basket

        Returns:
            list[Store] | None: list of visited stores
        """        
        if len(self.basket) > 0:
            return self.basket["store"].unique().tolist()
        
    
    def get_idx_of_identical_item_df(self,item:pd.Series, df:pd.DataFrame) -> None | int :
        """Helper function to get the idx of an item in df. 

        Args:
            item (pd.Dataframe): item to be found 
            df (pd.Dataframe): df to look for the item for

        Returns:
            int | None: index of item or none, if item is not in df
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