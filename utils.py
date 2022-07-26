#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom functions
"""

import pickle as pkl
import pandas as pd

def load_data (file) : 
    """
    Loads a .pkl file 

    Parameters
    ----------
    file : str
        File name for .pkl file, including file path with respect to working
        directory
        
    Returns
    -------
    Object of any type imported from file
    """
    
    with open(file, "br") as f:
         data = pkl.load(f)
         
    return data

def save_data (file, element) : 
    """
    Save an object

    Parameters
    ----------
    file : str
        File name for .pkl file, including file path with respect to working
        directory and extension .pkl
        
    element : any type
        Object to be saved
    """
    
    with open(file, "bw") as f:
         pkl.dump(element, f)
         
def format_raw_data (df_old, res_IDs):
    """
    Formats raw data imported from ISSDA .csv and .txt files
    
    Column dtypes are downcast to lower-memory versions; new columns for day 
    and time codes are generated based on the column "day_time_code"; 
    non-residential instances are removed.

    Parameters
    ----------
    df_old : pandas.core.frame.DataFrame
        Dataset containing the columns "ID", "day_time_code" and "consumption"
        
    res_IDs : list
        ID numbers for instances classified as "residential" consumers

    Returns
    -------
    pandas.core.frame.DataFrame
        Dataset containing only residential data, with columns "ID", 
        "day_time_code", "consumption", "day_code" and "time_code". For more 
        information on the codes used for "day_time_code", etc., visit
        https://www.ucd.ie/issda/data/commissionforenergyregulationcer/ .
    """
    
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
