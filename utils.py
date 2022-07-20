#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generic custom functions
"""

import pickle as pkl
import pandas as pd

def load_data (file) : 
    
    with open(file, "br") as f:
         data = pkl.load(f)
    return data

def save_data (file, element) : 
    
    with open(file, "bw") as f:
         pkl.dump(element, f)
         
def format_raw_data (df_old, res_IDs):
    
    df = df_old.copy()
    
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
    
    return df_sub
