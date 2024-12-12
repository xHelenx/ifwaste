from __future__ import annotations
import logging
import random
from typing import List

import numpy as np
from Grid import Grid
import pandas as pd
from Storage import Storage
from Store import Store
import globals
from BasketCurator import BasketCurator
from DealAssessor import DealAssessor
from FoodGroups import FoodGroups

class HouseholdShoppingManager: 
    
    def __init__(self, budget:float, pantry:Storage, fridge:Storage, req_servings_per_fg, grid:Grid, household:Household, # type: ignore
                 shopping_freq, time:list[float], datalogger:DataLogger, id:int, logger:logging.Logger|None) -> None: # type: ignore
        from Household import Household
        self.pantry:Storage = pantry
        self.fridge:Storage = fridge
        self.logger: logging.Logger|None = logger
        
        self.grid = grid
        self.location:Household = household
        self.datalogger = datalogger
        self.id:int = id
        
        self.budget:float = budget
        self.time:list[float]= time
        
        ### SHOPPING CHARACTERISTICS
        self.shopping_frequency:int = shopping_freq
        self.price_sens:float = random.uniform(0,1)
        self.brand_sens: float = random.uniform(0,1)
        self.brand_pref: dict[Store,float]  = {store:random.uniform(0,1) for store in globals.NEIGHBORHOOD_STORE_TYPES}
        self.quality_sens: float  = random.uniform(0,1)
        self.availability_sens: float  = random.uniform(0,1)
        self.deal_sens: float  = random.uniform(0,1)
        self.planner: float = random.uniform(0,1)
        self.impulsivity:float = random.uniform(0,1)
        
        sum_sens = self.price_sens + self.brand_sens + self.quality_sens + self.availability_sens + self.deal_sens
        self.price_sens /= sum_sens
        self.brand_sens /= sum_sens
        self.quality_sens /= sum_sens
        self.availability_sens /= sum_sens
        self.deal_sens /= sum_sens
        
        self.todays_budget:float = 0
        self.todays_time:float = 0
        self.req_servings_per_fg = req_servings_per_fg
        self.req_servings:float = sum(self.req_servings_per_fg.values())
    
    def _get_what_to_buy(self) -> pd.Series: 
        required_servings = dict()
        required_servings.update((x, y*self.shopping_frequency) for x, y in self.req_servings_per_fg.items())
        required_servings = pd.Series(required_servings)
        fridge_content = pd.Series(self.fridge.get_servings_per_fg())
        pantry_content = pd.Series(self.pantry.get_servings_per_fg())
    
        return required_servings - (fridge_content + pantry_content)
   
    def _get_budget_for_this_purchase(self) -> float: #estimate budget for current shopping tour
        days_till_payday = globals.NEIGHBORHOOD_PAY_DAY_INTERVAL - (globals.DAY % globals.NEIGHBORHOOD_PAY_DAY_INTERVAL)   
        if days_till_payday >= self.shopping_frequency: #we are staying within this months budget plans:
            if self.todays_budget <= 0: #no money to buy anything
                return 0 
            req_servings_till_payday = (self.req_servings * days_till_payday) - (self.fridge.get_total_servings() + self.pantry.get_total_servings())
            req_daily_servings = req_servings_till_payday/days_till_payday
            price_per_serving = self.todays_budget/req_servings_till_payday
            return price_per_serving * (req_daily_servings * self.shopping_frequency) * globals.HH_OVER_BUDGET_FACTOR

        else: #hh will receive new money, so the budget estimate has to consider it
            #TODO remember for report: that now the budget is a bit higher, because we split the money along the whole month
            still_have_servings = self.fridge.get_total_servings() + self.pantry.get_total_servings()
            days = days_till_payday + globals.NEIGHBORHOOD_PAY_DAY_INTERVAL
            req_daily_servings = (self.req_servings*days - still_have_servings)/(days)
            
            budget_before_pd = self.todays_budget
            if self.todays_budget <= 0:
                budget_before_pd = 0
            total_budget = budget_before_pd + self.budget 
            
            price_per_serving = total_budget/(req_daily_servings*days)
            
            return price_per_serving * req_daily_servings * days_till_payday

    def _convert_bought_to_store_series(self,item:pd.Series, status:str) -> pd.Series:
        price = 0.0
        inedible = 0
        for fg in FoodGroups.get_instance().get_all_food_groups():
            #assumes you can buy only one item type items
            if fg != item["type"]: 
                item[fg] = 0.0
            else:
                item[fg] = float(item["servings"])
                price = item["servings"] * item["price_per_serving"]
                inedible = FoodGroups._instance.food_groups.loc[FoodGroups._instance.food_groups["type"] == item["type"], "inedible_percentage"].values[0] # type: ignore
        if "adjustment" in item.index: 
            item = item.drop(["adjustment"])
        if "impulse_buy_likelihood" in item.index: 
            item = item.drop(["impulse_buy_likelihood"])
        item = item.drop(["type", "price_per_serving","sale_type", "deal_value", "store", "discount_effect", "sale_timer",
                        "product_ID", "amount"])
        item["status"] = status
        item["price"] = price
        item["inedible_percentage"] = inedible #assuming item is exactly on fg
        
        return item
        
        
    def _store_groceries(self, basket:pd.DataFrame) -> None: 
        #put groceries away
        for idx in basket.index:
            self.datalogger.append_log(self.id,"log_bought", basket.loc[idx])
            item = basket.loc[idx].copy()
            
            status = storage = None
            if item["type"] == globals.FGSTOREPREPARED:
                status = globals.STATUS_PREPREPARED
                storage = self.fridge
            else: 
                status = globals.STATUS_UNPREPARED
                storage = self.pantry
            
            amount = item["amount"]    
            item = self._convert_bought_to_store_series(item=item, status=status)
            for _ in range(amount):
                storage.add(item=item)
            
    def _choose_second_store(self, is_planner:bool, selected_stores:list[Store], servings_to_buy_fg:pd.Series) -> Store | None: 
        store = None
        avail_fgs = selected_stores[0].get_available_food_groups()
        relevant_fg = servings_to_buy_fg[servings_to_buy_fg> 0].index.tolist()
        left_fg = [i for i in relevant_fg if i not in avail_fgs]
        if len(left_fg) > 0: 
            store = self.choose_a_store(is_planner=is_planner, selected_store=selected_stores, required_fgs=left_fg) #TODO it was left_fg[0], dunno why

        return store
        
    def shop(self, is_quickshop:bool=False) -> float:
        """Shops for groceries and stores them in the correct location in the house
        """ 
        if is_quickshop:
            globals.log(self,"------> QUICK SHOPPING")    
        else:
            globals.log(self,"------> SHOPPING")
            
        self.todays_time = self.time[globals.DAY%7] 
        budget = self._get_budget_for_this_purchase() 
        is_planner = self.planner > random.uniform(0,1)
        
        if is_quickshop: 
            relevant_fg = [globals.FGSTOREPREPARED]
        else: 
            servings_to_buy_fg = self._get_what_to_buy()
            relevant_fg = servings_to_buy_fg[servings_to_buy_fg> 0].index.tolist()
            
        selected_stores = []
        store = self.choose_a_store(is_planner=is_planner, selected_store=selected_stores,required_fgs=relevant_fg)
        if store != None and not store in selected_stores: 
            selected_stores.append(store)
        else:
            globals.log(self,"No store found, avail time %f", self.todays_time)
            return 0
        
        
        if is_quickshop: 
            #build quick basket
            basketCurator = BasketCurator(stores=selected_stores, logger=self.logger, budget=budget)
            basketCurator.create_basket(is_quickshop=True)
        else: 
            if servings_to_buy_fg.sum() <= 0: # type: ignore #we dont need to buy anything
                return 0
            
            #if planner add more stores if necessary because of missing fg
            if is_planner: #planner hh 
                store = self._choose_second_store(is_planner,selected_stores,servings_to_buy_fg) # type: ignore
            if not store is None and not store in selected_stores: 
                selected_stores.append(store)     

            #create initial basket with groceries
            basketCurator = BasketCurator(stores=selected_stores, servings_to_buy_fg=servings_to_buy_fg, budget=budget, logger=self.logger) # type: ignore
            basketCurator.create_basket()
        
            self._handle_basket_adjustment(is_planner,basketCurator,selected_stores,budget, servings_to_buy_fg)                                            # type: ignore

        #globals.log(self,basketCurator.basket)    
        #calculated required time for shopping tour (final time for planner, current time for not planner)
        visited_stores = basketCurator.get_visited_stores()
        duration = 0
        if visited_stores != None:
            coords = [store.get_coordinates() for store in visited_stores]
            duration += self.grid.get_travel_time_entire_trip(self.location,coords)            
        
        basketCurator.impulse_buy(self.impulsivity)
        
        if len(basketCurator.basket) > 0:
            globals.log(self,"FINAL BASKET: items %i, cost: %f", basketCurator.basket["amount"].sum(), (basketCurator.basket["price_per_serving"] * basketCurator.basket["amount"] * basketCurator.basket["servings"] ).sum())
        else:
            globals.log(self,"FINAL BASKET is empty")
        
        if len(basketCurator.basket) > 0:
            self._pay(basket=basketCurator.basket) #todo stock was empty once so nothing was bought?! origing of problem?
            self._store_groceries(basket=basketCurator.basket)
            
        globals.log(self,"BOUGHT: %i", sum(basketCurator.basket["servings"]*basketCurator.basket["amount"]))
            
        return duration
        
    def _pay(self, basket:pd.DataFrame) -> None: 
        spent = (basket["price_per_serving"] * basket["servings"] * basket["amount"]).sum()
        self.todays_budget -= spent
        globals.log(self, "spent %s of budget, left: %s", str(spent), str(self.todays_budget) )
        
        
    def _handle_basket_adjustment(self,is_planner, basketCurator:BasketCurator, selected_stores:list[Store],
        budget:float, servings_to_buy_fg:pd.Series) -> BasketCurator: 

        if self._is_adjustment_needed(basketCurator): 
            if is_planner: 
                basketCurator.adjust_basket()
            else: 
                if random.uniform(0,1) > 0.5 and len(selected_stores) < 2: 
                    if not basketCurator.is_basket_in_budget(): 
                        store = self.choose_a_store(is_planner=is_planner, selected_store=selected_stores, needs_lower_price=True)
                        if store != None and store not in selected_stores:
                                selected_stores.append(store)
                                #redo entire basket now with a bonus store
                                basketCurator.return_basket_to_store() #we are starting over instead
                                basketCurator = BasketCurator(stores=selected_stores, servings_to_buy_fg=servings_to_buy_fg, budget=budget, logger=self.logger)
                                basketCurator.create_basket()
                    if not basketCurator.does_basket_cover_all_fg(): 
                        if random.uniform(0,1) > 0.5 and len(selected_stores) < 2:
                            #adding a store from a lower price group
                            store = self.choose_a_store(is_planner, selected_stores, required_fgs=basketCurator.get_missing_fgs())
                            if store != None and store not in selected_stores:
                                    selected_stores.append(store)
                                    basketCurator.stores.append(store)
                                    #buy missing food items + keep old basket #TODO is this ok?
                                    basketCurator.create_basket()
        if self._is_adjustment_needed(basketCurator): 
            basketCurator.adjust_basket()
            
        return basketCurator

    def _is_adjustment_needed(self, basketCurator:BasketCurator) -> bool:
        return not basketCurator.is_basket_in_budget()  or not basketCurator.does_basket_cover_all_fg()

    
    def choose_a_store(self,is_planner,selected_store:list[Store], required_fgs:List[str] | None =None, needs_lower_price: bool=False) -> None | Store:
        assert not (required_fgs == None and needs_lower_price == None) #TODO technically ok now
        selection = None 
        if len(selected_store) == 0: #no store is selected
            store_options = self.grid.get_stores_within_time_constraint(self.location,self.todays_time)
        else: #a store has been selected
            store_options = self.grid.get_second_store_within_time_constraint(self.location,selected_store[0],self.todays_time,fg=required_fgs, needs_lower_price=needs_lower_price)
        #choose a store from possible options (not is_planner just selects 1 store here)
        if len(store_options) > 0:
            store_order = self._get_store_order(is_planner, required_fgs,store_options)
            selection = self._wheel_selection(store_order)
            while selection in selected_store: 
                if len(store_order) > 0: 
                    selection = self._wheel_selection(store_order)
                    store_order = store_order.drop(selection)
                else:
                    return None
        return selection
        
    def _wheel_selection(self, item:pd.Series, num_selections=1): 
        maxVal = item.sum()
        probabilities = item / maxVal
        cumulative_probabilities = probabilities.cumsum()
        
        indices = []
        for _ in range(num_selections):
            rand = np.random.random()
            selected_index = cumulative_probabilities[cumulative_probabilities >= rand].index[0]
            indices.append(selected_index)
        return indices[0]
        
    def _get_store_order(self, is_planner, relevant_fg,stores): 
        store_preference = pd.Series({store:0.0 for store in stores})
        
        if not is_planner: 
            for store in stores: #we only take 3 in account here, but as we do it everywhere its fine that it 
                #cant reach 1
                preference = (self.quality_sens * store.quality + self.price_sens * (1-store.price) +\
                    self.brand_sens * self.brand_pref[store.store_type.value])
                store_preference[store] = preference
        else: 
            dealAssessor = DealAssessor()
            best_deals = dealAssessor.assess_best_deals(stores)
            
            for store in stores: 
                #assert not store.stock.empty #TODO sometimes it is empty, should this be handled or do we ignore it?
                
                local_deal = dealAssessor.assess_best_deals([store])
                deal = 0
                deal = dealAssessor.calculate_deal_value(relevant_fg, local_deal, best_deals)
                    
                avail_fg_value  = 0
                if relevant_fg != None: 
                    avail_fg = store.get_available_food_groups()   
                    avail_fg_value  = len(relevant_fg)/len(avail_fg)

                preference = (self.quality_sens * store.quality + self.price_sens * (1-store.price) +\
                    self.brand_sens * self.brand_pref[store.store_type.value] + self.deal_sens *\
                        deal + self.availability_sens *avail_fg_value)
                store_preference[store] = preference
                
        return store_preference