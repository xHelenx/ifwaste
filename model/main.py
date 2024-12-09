import logging
import os
from Neighborhood import Neighborhood
import globals
import argparse
import pandas as pd

def main(name:str) -> None:
    #read configuration file 
    #os.chdir(r"E:/UF/ifwaste/model")
    os.chdir(r"/blue/carpena/haasehelen/ifwaste/model")
    globals.configure_simulation(file=name)     
    pd.set_option("display.max_rows", None)     # Show all rows
    pd.set_option("display.max_columns", None)  # Show all columns
    pd.set_option("display.width", 300)         # Set max characters per line

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
