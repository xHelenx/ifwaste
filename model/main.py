import logging
from Neighborhood import Neighborhood
import globals


#read configuration file 
globals.configure_simulation()

#setup logging -> logging file is generated as "debug.log" in ifwaste folder
if globals.SIMULATION_DEBUG_LOG_ON:
    logging.getLogger(__name__)
    logging.basicConfig(filename="debug.log",encoding="utf-8",level=logging.DEBUG, filemode="w")

for run in range(0,globals.SIMULATION_RUNS): 
    print("Start run", run )
    
    #setup neighborhood  
    neighborhood = Neighborhood()
    print(neighborhood.grid)
    
    #run simulation
    neighborhood.run(run_id=run)
   
