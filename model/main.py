import json
import os
from pathlib import Path
from Neighborhood import Neighborhood
import globals_config as globals_config
import argparse
import pandas as pd
import sys

def load_selected_samples(file, selected_lines):
    with open(file, 'r') as f:
        lines = f.readlines()

    selected_data = []
    for idx in selected_lines:
        if idx < len(lines):
            row = lines[idx].strip().split('\t')
            selected_data.append(row)

    # Transpose the rows into columns
    transposed = list(map(list, zip(*selected_data)))
    if "sens_class" in transposed[0]:
        transposed = transposed[1:]
    return transposed #remove sens class


def parse_line_selector(selector, file):
    result = []
    for s in selector:
        if ':' in s:
            start, end = map(int, s.split(':'))
            result = list(range(start, end))
        elif selector == "all":
            with open(file, 'r') as f:
                #num_lines = sum(1 for _ in f)
                num_lines = len(f.readlines())
                result = list(range(num_lines))
        else:
            result = [int(s)]
    return result

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
    parser.add_argument('--sim_run_id', nargs='+', help='TBD')
    
    parser.add_argument('--config_path', type=str, help='Path to JSON config file')
    # Option 2: Provide values directly
    parser.add_argument('--nh_values', nargs='+', help='List of neighborhood level input values passed directly')
    parser.add_argument('--hh_values', nargs='+', help='List of household level input values passed directly')
    parser.add_argument('--sim_values', nargs='+', help='List of simulation level (constants) input values passed directly')
    parser.add_argument('--path', nargs='+', help='TBD')
    # Option 3: Provide the path and the relevant intervals
    
    parser.add_argument('--hh_id', nargs='+', help='TBD')
    parser.add_argument('--nh_id', nargs='+', help='TBD')
    
    parser.add_argument('--full_csv', action='store_true', help='TBD')
    parser.add_argument('--agg_csv', action='store_true', help="TBD")
    
    try:
        args = parser.parse_args()
    except SystemExit as e:
        print("Argument parsing failed:", e)
        sys.exit(1)
        
        
    globals_config.LOG_ALL_OUTPUT = args.full_csv
    globals_config.LOG_AGG_OUTPUT = args.agg_csv

    simulation_run_id = args.sim_run_id
    pd.set_option("display.max_rows", None)     # Show all rows
    pd.set_option("display.max_columns", None)  # Show all columns
    pd.set_option("display.width", 300)         # Set max characters per line

    if args.config_path: 
        #read configuration file 
        #os.chdir(r"E:/UF/ifwaste/model")z
        #os.chdir(r"/blue/carpena/haasehelen/ifwaste/bash-scripts/experiments")
        print("ARGS PATH:", args.config_path)
        globals_config.configure_simulation(file=args.config_path) 
    elif args.nh_values and args.hh_values and args.sim_values:
        all_header_files = [
            f for f in Path(args.path).glob("*.txt")
            if "header" in f.name
        ]
        all_header_files = sorted(all_header_files, key=lambda x: x.name[0]) #sort alphabetical by currnet layer to match header and values
        
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
        
        globals_config.configure_simulation(as_dict=config) 
    elif args.path and args.nh_id and args.hh_id:
        #if not os.path.isfile(args.nh_path):
        #    raise ValueError("You must provide a valid --nh_path.")
        all_header_files = [
            f for f in Path(args.path[0]).glob("*.txt")
            if "header" in f.name
        ]
        all_header_files = sorted(all_header_files, key=lambda x: x.name[0])#sort alphabetical by currnet layer to match header and values
        
        hh_ids = parse_line_selector(args.hh_id[0], args.path[0]+ globals_config.SAMPLE_FILENAME_HH)
        nh_ids = parse_line_selector(args.nh_id[0], args.path[0] + globals_config.SAMPLE_FILENAME_NH)
        sim_ids = parse_line_selector("all", args.path[0] + globals_config.SAMPLE_FILENAME_SIM)
        ##HEADER 
        keys = []
        for file in all_header_files:
            with open(file) as f:
                keys += [line.strip() for line in f if line.strip()]
        ###DATA
        #arg_values = args.hh_values + args.nh_values + args.sim_values #alphabetical!
        files = [args.path[0]+globals_config.SAMPLE_FILENAME_HH, 
                args.path[0]+globals_config.SAMPLE_FILENAME_NH, 
                args.path[0]+globals_config.SAMPLE_FILENAME_SIM]
        ids = [hh_ids, nh_ids, sim_ids]
        values = []
        for id,file in zip(ids,files):
            with open(file, "r") as f: 
                values += load_selected_samples(file, id)

        if len(keys) != len(values):
            raise ValueError("Mismatch between number of values and keys in structure file.")

        flat_dict = dict(zip(keys, values))
        config = unflatten_dict(flat_dict)
        print(config)
        
    else:
        raise ValueError("Check parameter list passed")
        
    
    globals_config.configure_simulation(simulation_run_id,as_dict=config)     
    #setup neighborhood  
    neighborhood = Neighborhood()
    print(neighborhood.grid)
    
    #run simulation
    neighborhood.run()
