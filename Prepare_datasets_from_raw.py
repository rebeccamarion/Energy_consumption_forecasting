# -*- coding: utf-8 -*-
"""
Script for transforming data from Data_raw folder into the data in Data folder
"""

import pandas as pd
import glob 
import os
import utils

##########################
#### ELECTRICITY DATA ####
##########################

file_path_raw_data = "Data_raw/Electricity/"
file_path_data = "Data/Electricity/"


## Meta data (meter ids, building type, etc) ##

file_name_meta_data = file_path_raw_data + 'SME and Residential allocations.xlsx'
df = pd.read_excel(file_name_meta_data)
meta_data = df.iloc[:, 0:4]
# Residential: Code = 1
res_IDs = list(meta_data.loc[meta_data.Code == 1, "ID"]) # IDs for residential 

## Consumption data ##

file_names_consum_data = sorted(glob.glob(os.path.join(file_path_raw_data, "*.txt")))
nb_files = len(file_names_consum_data)

df_list = list()
for file_index in range(nb_files):
    
    print('\n processing file %d of %d' % (file_index + 1, nb_files))
    
    file_name_consum_data = file_names_consum_data[file_index]
    
    df = pd.read_csv(file_name_consum_data, sep=" ", header = None)
    df.columns = ["ID", "day_time_code", "consumption"]

    #df.memory_usage(deep=True)
    # reduce memory required for each column
    df["ID"] = df["ID"].astype("category")
    df["day_time_code"] = pd.to_numeric(df["day_time_code"], downcast="unsigned")
    df["consumption"] = pd.to_numeric(df["consumption"], downcast="float")

    # add separate columns for day and time codes
    new_var = df[['day_time_code']].to_numpy().astype('U6').view('U3').astype(int)
    new_var_df = pd.DataFrame(new_var, columns = ["day_code", "time_code"])
    df = df.join(new_var_df)

    # reduce memory required for new columns
    df["day_code"] = pd.to_numeric(df["day_code"], downcast="unsigned")
    df["time_code"] = pd.to_numeric(df["time_code"], downcast="unsigned")

    # Keep residential data only
    df_sub = df.loc[df['ID'].isin(res_IDs), :].reset_index(drop = True) # reset index to avoid increasing memory
    df_list.append(df_sub)

df_all = pd.concat(df_list).reset_index(drop = True) 
df_all = df_all.sort_values(['ID', 'day_time_code'], ascending=[True, True]).reset_index(drop = True)

file_name_out = file_path_data + "residential_all.pkl"
utils.save_data(file_name_out, df_all)
