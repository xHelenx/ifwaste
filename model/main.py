import logging
import os
from Neighborhood import Neighborhood
import globals
import argparse

def main(name:str) -> None:
    #read configuration file 
    os.chdir(r"E:/UF/ifwaste/model")
    globals.configure_simulation(file=name)
    globals.setup_logger()

    for run in range(0,globals.SIMULATION_RUNS): 
        print("Start run", run )
        
        #setup neighborhood  
        neighborhood = Neighborhood()
        print(neighborhood.grid)
        
        #run simulation
        neighborhood.run(run_id=run)
    

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--config_path', type=str, 
                        default=globals.CONFIG_PATH,  # Set your default config path here
                        help="Relative path to the configuration file used (default: config.json)")
    
    args = parser.parse_args()
    main(args.config_path)


def log(logger, message) -> None: 
    if globals.SIMULATION_DEBUG_LOG_ON: 
        logger.debug(message)