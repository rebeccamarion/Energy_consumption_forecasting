#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom functions
"""

import pickle as pkl
import pandas as pd
import numpy as np

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
         
def agg_consumption_dst_hours (x, dst_times):
    
    """
    Aggregates consumption data for the repeated hour at the end of daylight
    savings time (DST) 
    
    Replaces consumption for the hour before DST ends with the mean of consumption 
    before and after (at the equivalent time points). Removes data for the hour 
    after DST ends. Shifts the remaining time codes downwards.
    

    Parameters
    ----------
    x : pandas.core.frame.DataFrame
        Dataset containing the columns "ID", "day_time_code", "consumption", 
        "day_code" and "time_code" (instances for a single ID and day_code for
        for a day where DST ends)
        
    dst_times : dict
        time codes related to the repeated hour at the end of daylight savings
        time (DST), with keys "before" and "after" with values equal to the time
        codes in the hour before and after DST ends

    Returns
    -------
    pandas.core.frame.DataFrame
        Dataset without the extra hour resulting from the end of DST
        
    """
    
    # Sort dataset by time_code
    x = x.sort_values(['time_code'], ascending=[True]).reset_index(drop = True)
    
    # Identify indexes for the hour before and after DST ends
    wh_before = x.time_code.isin(dst_times["before"])
    wh_after = x.time_code.isin(dst_times["after"])
    
    # Aggregate the consumption levels (before and after, mean)
    consumption_vals = np.array([x.loc[wh_before, "consumption"], x.loc[wh_after, "consumption"]])
    mean_consumption_vals = np.mean(consumption_vals, axis = 0)
    
    # Update the consumptions values for the hour before DST ends
    x.loc[wh_before, "consumption"] = mean_consumption_vals
    
    # Remove the rows for the hour after DST ends
    x = x.loc[np.logical_not(wh_after), :]
    
    # Shift the remaining time codes downwards
    wh_shift = x.time_code > np.max(dst_times["after"])
    x.loc[wh_shift, "time_code"] = x.loc[wh_shift, "time_code"] - len(dst_times["after"])
    
    return x

def interpolate_consumption_dst_hours(x):
    """
    Adds rows for missing time codes and interpolates missing consumption values  

    Parameters
    ----------
    x : pandas.core.frame.DataFrame
        Dataset containing the columns "ID", "day_time_code", "consumption", 
        "day_code" and "time_code" (instances for a single ID and day_code for
        for a day where DST begins)

    Returns
    -------
    pandas.core.frame.DataFrame
        Dataset with added rows for missing time codes (consumption interpolated)
        
    """
    # Sort dataset by time_code
    x = x.sort_values(['time_code'], ascending=[True]).reset_index(drop = True)
    
    # Missing time codes
    time_code_min = x.time_code.min()
    time_code_max = x.time_code.max()
    all_time_codes = set(np.arange(time_code_min, time_code_max + 1))
    observed_time_codes = set(x.time_code)
    missing_time_codes = list(all_time_codes.difference(observed_time_codes))
    
    # Create rows for missing time codes
    x_missing = x.iloc[range(len(missing_time_codes)), :].copy()
    x_missing.consumption = np.nan
    x_missing.time_code = missing_time_codes
    day_code_str = x_missing.day_code.astype(str).apply(lambda y: y.zfill(3))
    time_code_str = x_missing.time_code.astype(str).apply(lambda y: y.zfill(2))
    x_missing.day_time_code = (day_code_str + time_code_str).astype(int)
    
    # Add missing rows to x
    x = pd.concat([x, x_missing]).sort_values(['time_code'], ascending=[True]).reset_index(drop = True)
    
    # Interpolate missing consumption values
    x.consumption = x.consumption.interpolate()
    
    return x
    
         
def format_raw_data (df_old, res_IDs, dst_days, dst_times):
    """
    Formats raw data imported from ISSDA .csv and .txt files
    
    Column dtypes are downcast to lower-memory versions; new columns for day 
    and time codes are generated based on the column "day_time_code"; 
    non-residential instances are removed; days where DST begins and ends are
    processed using the functions interpolate_consumption_dst_hours() and 
    agg_consumption_dst_hours(); instances (meters) with missing days/times
    are removed.

    Parameters
    ----------
    df_old : pandas.core.frame.DataFrame
        Dataset containing the columns "ID", "day_time_code" and "consumption"
        
    res_IDs : list
        ID numbers for instances classified as "residential" consumers
    
    dst_days : dict
        day codes related to daylight savings time (DST), with keys "end" for 
        day codes indicating the end of DST and "beg" for the beginning of DST
        
    dst_times : dict
        time codes related to the repeated hour at the end of daylight savings
        time (DST), with keys "before" and "after" with values equal to the time
        codes in the hour before and after DST ends

    Returns
    -------
    pandas.core.frame.DataFrame
        Dataset containing only residential data, with columns "ID", 
        "day_time_code", "consumption", "day_code" and "time_code". For more 
        information on the codes used for "day_time_code", etc., visit
        https://www.ucd.ie/issda/data/commissionforenergyregulationcer/ . 
        
    """
    
    df = df_old.copy()
    
    # Keep residential data only
    df = df.loc[df['ID'].isin(res_IDs), :].reset_index(drop = True) # reset index to avoid increasing memory
    
    #df.memory_usage(deep=True)
    # Reduce memory required for each column
    df["ID"] = df["ID"].astype("category")
    df["day_time_code"] = pd.to_numeric(df["day_time_code"], downcast="unsigned")
    df["consumption"] = pd.to_numeric(df["consumption"], downcast="float")

    # Add separate columns for day and time codes
    new_var = df[['day_time_code']].to_numpy().astype('U6').view('U3').astype(int)
    new_var_df = pd.DataFrame(new_var, columns = ["day_code", "time_code"])
    df = df.join(new_var_df)

    # Reduce memory required for new columns
    df["day_code"] = pd.to_numeric(df["day_code"], downcast="unsigned")
    df["time_code"] = pd.to_numeric(df["time_code"], downcast="unsigned")
    
    # Check for missing day/times for each ID
    day_time_count_df = df.groupby("ID", as_index = False).apply(lambda x: x.day_time_code.nunique())
    day_time_count_df = day_time_count_df.rename(columns = {None: "counts"})
    # Remove instances with missing days and/or times
    max_count = day_time_count_df.loc[:, "counts"].max()
    IDs_without_missing = set(day_time_count_df.loc[day_time_count_df.counts == max_count, "ID"])
    df = df.loc[df['ID'].isin(IDs_without_missing), :].reset_index(drop = True)
    
    # Split data into non-DST days and DST-end and DST-beg days
    all_dst_days = [item for sublist in dst_days.values() for item in sublist]
    df_non_dst = df.loc[np.logical_not(df.day_code.isin(all_dst_days)), :]
    df_dst_end = df.loc[df.day_code.isin(dst_days["end"]), :]
    df_dst_beg = df.loc[df.day_code.isin(dst_days["beg"]), :]
    
    # Aggregate data for repeated hour on days where DST ends 
    grouped_dst_end = df_dst_end.groupby(["ID", "day_code"], as_index = False)
    df_dst_end = grouped_dst_end.apply(lambda x: agg_consumption_dst_hours(x, dst_times)).reset_index(drop = True)

    # Add rows for lost hour on days where DST begins and interpolate missing values
    grouped_dst_beg = df_dst_beg.groupby(["ID", "day_code"], as_index = False)
    df_dst_beg = grouped_dst_beg.apply(lambda x: interpolate_consumption_dst_hours(x)).reset_index(drop = True)
    
    # Concatenate all sub dfs
    df = pd.concat([df_non_dst, df_dst_end, df_dst_beg]).reset_index(drop = True)
   
    # Transform day_code to date
    df["date"] = pd.to_datetime(df["day_code"], unit='D', origin='2008-12-31')
    
    # Tranform time_code to time
    df["time"] = pd.TimedeltaIndex(df['time_code']*30, unit='m')
    
    # Create date-time timestamp column
    df["date_time"] = df["date"] + df["time"] 
    
    return df

def agg_hourly_data (df, ID = None, col_name = "consumption"):
    """
    Aggregates (sums) all data in an hour period for a single series

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        Dataset containing a column to aggregate (with the name col_name) and
        index of time stamps
        
    ID : int
        ID number for the series in df
    
    col_name : str
        name of column that is aggregated
        

    Returns
    -------
    pandas.core.series.Series
        Dataset of values for col_name aggregated hourly (sum). 
        
    """
    
    series = df[col_name]
    series_agg = series.resample("60min", label='right', closed='right').sum()
    series_agg = series_agg.rename(ID, inplace = True)

    return series_agg    
