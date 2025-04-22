import json
import os
from pathlib import Path
from Neighborhood import Neighborhood
import globals
import argparse
import pandas as pd
import sys


def unflatten_dict(flat_dict, sep=":"):
    nested = {}
    for compound_key, value in flat_dict.items():
        keys = compound_key.split(sep)
        d = nested
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value
    return nested
    

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(description="Run simulation with config or direct values")
    parser.add_argument('--config_path', type=str, help='Path to JSON config file')
    # Option 2: Provide values directly
    parser.add_argument('--nh_values', nargs='+', help='List of neighborhood level input values passed directly')
    parser.add_argument('--hh_values', nargs='+', help='List of household level input values passed directly')
    parser.add_argument('--sim_values', nargs='+', help='List of simulation level (constants) input values passed directly')
    parser.add_argument('--sample_path', type=str, help='Structure file for values (used with --values)')

    try:
        args = parser.parse_args()
    except SystemExit as e:
        print("Argument parsing failed:", e)
        sys.exit(1)


    pd.set_option("display.max_rows", None)     # Show all rows
    pd.set_option("display.max_columns", None)  # Show all columns
    pd.set_option("display.width", 300)         # Set max characters per line

    if args.config_path: 
        #read configuration file 
        #os.chdir(r"E:/UF/ifwaste/model")z
        #os.chdir(r"/blue/carpena/haasehelen/ifwaste/bash-scripts/experiments")
        print("ARGS PATH:", args.config_path)
        globals.configure_simulation(file=args.config_path) 
    else:
        if not args.sample_path or not os.path.isdir(args.sample_path):
            raise ValueError("You must provide a valid --sample_path when using --values.")
        
        all_header_files = [
            f for f in Path(args.sample_path).glob("*.txt")
            if "header" in f.name
        ]
        all_header_files = sorted(all_header_files, key=lambda x: x.name[0])#sort alphabetical by currnet layer to match header and values
        
        keys = []
        for file in all_header_files:
            with open(file) as f:
                keys += [line.strip() for line in f if line.strip()]
        
        arg_values = args.hh_values + args.nh_values + args.sim_values #alphabetical!
        if len(keys) != len(arg_values):
            raise ValueError("Mismatch between number of values and keys in structure file.")

        flat_dict = dict(zip(keys, arg_values))
        config = unflatten_dict(flat_dict)
        print(config)
        globals.configure_simulation(as_dict=config) 
        
    #run simulation        
    for run in range(0,globals.SIMULATION_RUNS): 
        print("Start run", run)
        
        #setup neighborhood  
        neighborhood = Neighborhood()
        print(neighborhood.grid)
        
        #run simulation
        neighborhood.run(run_id=run)
    
    
