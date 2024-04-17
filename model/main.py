import json 
import logging
from Neighborhood import Neighborhood
from House import House
import globals

#setup logging -> logging file is generated as "debug.log" in ifwaste folder
logging.getLogger(__name__)
logging.basicConfig(filename="debug.log",encoding="utf-8",level=logging.DEBUG, filemode="w")

#read configuration file 
globals.configure_simulation() 

for run in range(0,globals.SIMULATION_RUNS): 
    print("Start run", run )
    houses = []
    assert globals.NEIGHBORHOOD_HOUSES >= globals.NEIGHBORHOOD_SERVING_BASED 
    for i in range(0,globals.NEIGHBORHOOD_SERVING_BASED): 
       houses += [House(i,is_serving_based=True)] 
    for i in range(globals.NEIGHBORHOOD_SERVING_BASED,globals.NEIGHBORHOOD_HOUSES): 
        houses += [House(i,is_serving_based=False)] 
        
    #setup neighborhood  
    neighborhood = Neighborhood(houses=houses)
    #run simulation
    neighborhood.run(days=globals.SIMULATION_DAYS)
    #collect data
    neighborhood.data_to_csv(experiment_name=globals.EXPERIMENT_NAME, run=run)
    
