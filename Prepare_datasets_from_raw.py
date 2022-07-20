# -*- coding: utf-8 -*-
"""
Script for transforming data from Data_raw folder into the data in Data folder
"""

import glob 
import os
import pandas as pd

# custom functions
import utils

# Directories for raw data and processed data
prefix_raw = "Data_raw/"
prefix_data = "Data/"

##########################
#### ELECTRICITY DATA ####
##########################

data_type = "Electricity"
file_path_raw_data = prefix_raw + data_type + "/"
file_path_data = prefix_data + data_type + "/"


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
    
    df = pd.read_csv(file_name_consum_data, sep = " ", header = None)
    df.columns = ["ID", "day_time_code", "consumption"]

    df_sub = utils.format_raw_data(df_old = df, res_IDs = res_IDs)
    df_list.append(df_sub)

df_all = pd.concat(df_list).reset_index(drop = True) 
df_all = df_all.sort_values(['ID', 'day_time_code'], ascending=[True, True]).reset_index(drop = True)

file_name_out = file_path_data + "residential_all.pkl"
utils.save_data(file_name_out, df_all)

##################
#### GAS DATA ####
##################

data_type = "Gas"
file_path_raw_data = prefix_raw + data_type + "/"
file_path_data = prefix_data + data_type + "/"


## Meta data (meter ids, building type, etc) ##

file_name_meta_data = file_path_raw_data + 'Residential allocations.xls'
df = pd.read_excel(file_name_meta_data)
meta_data = df.iloc[:, 0:2]
# Residential: Code = 1
res_IDs = list(meta_data.ID) # IDs for residential 

## Consumption data ##

file_names_consum_data = sorted(glob.glob(os.path.join(file_path_raw_data, "*")))[0:-1]
nb_files = len(file_names_consum_data)

df_list = list()
for file_index in range(nb_files):
    
    print('\n processing file %d of %d' % (file_index + 1, nb_files))
    
    file_name_consum_data = file_names_consum_data[file_index]
    
    df = pd.read_csv(file_name_consum_data, sep = ",", header = 0)
    df.columns = ["ID", "day_time_code", "consumption"]
    
    df_sub = utils.format_raw_data(df_old = df, res_IDs = res_IDs)
    df_list.append(df_sub)

df_all = pd.concat(df_list).reset_index(drop = True) 
df_all = df_all.sort_values(['ID', 'day_time_code'], ascending=[True, True]).reset_index(drop = True)

file_name_out = file_path_data + "residential_all.pkl"
utils.save_data(file_name_out, df_all)
