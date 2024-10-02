from dask.diagnostics import ProgressBar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import dask.dataframe as dd
import os

PATH = os.getenv('PATH', 0)

def load_data() -> dict[str, dd.DataFrame]:
    # Dictionary to store DataFrames by main folder and CSV file type
    dataframes = {}

    # List of the main folders to process
    main_folders = [f for f in os.listdir(PATH) if os.path.isdir(os.path.join(PATH, f))]

    # CSV file types to be read
    csv_types = ['bought', 'config', 'daily', 'eaten', 'still_have', 'wasted']

    # Iterate over each main folder
    for main_folder in main_folders:
        folder_path = os.path.join(PATH, main_folder)
        
        # Initialize a dictionary to hold DataFrames for each CSV type within the main folder
        df_dict = {csv_type: [] for csv_type in csv_types}

        # Iterate over each run folder inside the main folder
        for run_folder in os.listdir(folder_path):
            run_path = os.path.join(folder_path, run_folder)
            if os.path.isdir(run_path):
                run_id = run_folder.split('_')[-1]  # Extract the run ID from the folder name
                
                # Read each CSV type and append the DataFrame to the respective list
                for csv_type in csv_types:
                    file_path = os.path.join(run_path, f'{csv_type}.csv')
                    if os.path.exists(file_path):
                        # Read the CSV file into a Dask DataFrame
                        df = dd.read_csv(file_path)
                        
                        # Check if 'House' column exists and modify it
                        if 'House' in df.columns:
                            df['House'] = run_id + "_" + df['House'].astype(str) 
                        if "Unnamed: 0" in df.columns: 
                            df = df.drop(columns=["Unnamed: 0"])
                        
                        #rename column in old version  
                        for item in df.columns: 
                            if "Day" in item: 
                                df = df.rename(columns={item:"Day"})                         
                        
                                                
                        # Append the modified DataFrame to the list
                        df_dict[csv_type].append(df)

        # Combine all runs into a single DataFrame for each CSV type
        combined_dfs = {csv_type: dd.concat(df_list, axis=0, ignore_index=True) 
                        for csv_type, df_list in df_dict.items()}
        
        # Store the combined DataFrames in the main dictionary under the main folder key
        dataframes[main_folder] = combined_dfs

    return dataframes


def calculate_average_daily(data, category:str):
    eaten_statistics = dict()
    people_df = pd.DataFrame()
    for main_folder, dfs in data.items():
        total_eaten = 0
        # Get the configuration DataFrame to calculate the number of people in each household
        config_df = dfs['config'].compute()
        # Compute the number of people per household (adults + children)
        idx = len(people_df)
        people_df.loc[idx, "Dataset"] = main_folder 
        people_df.loc[idx,"#People"] = config_df.iloc[0]["Adults"] + config_df.iloc[0]["Children"]
        # Load the eaten DataFrame
        eaten_df = dfs[category]
        
        # Filter for days > 14
        filtered_eaten_df = eaten_df[eaten_df['Day'] >= 14]
        filtered_eaten_df = filtered_eaten_df.compute()  # Compute the filtered DataFrame
        
        # Sum total eaten amounts and calculate the total people-days
        total_eaten += filtered_eaten_df['Kg'].sum()
        avg = total_eaten / (people_df.loc[people_df["Dataset"] == main_folder, "#People"] * (DAYS -14)* n_households)
        eaten_statistics.update({main_folder:avg})
    return eaten_statistics

