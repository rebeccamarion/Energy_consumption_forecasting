# About

This project includes code for processing energy consumption data accessed via 
the Irish Social Science Data Archive - www.ucd.ie/issda:

* Electricity Customer Behaviour Trial - Study Number (SN): 0012-00

The data are not accessible here, but may be requested directly from the ISSDA 
via a request form (https://www.ucd.ie/issda/data/commissionforenergyregulationcer/).

# Instructions

## Dependencies

The following packages are required to run the scripts in this project:

* glob
* numpy >= 1.22.3
* os
* pandas >= 1.4.1
* pickle

## Runing the Prepare_datasets_from_raw.py script

The following files from the ISSDA must be added before running the script
Prepare_datasets_from_raw.py:

* Data_raw/Electricity: add the files "File1.txt", ..., "File6.txt" and "SME and Residential allocations.xlsx"

# TO DO

In the future, code will be added to this project for the following to-do items:

* Exploratory analysis of the datasets
* Time series pre-processing
* Forecasting models

# Author(s)

All code was written by Rebecca Marion.

# References

Commission for Energy Regulation (CER). (2012). CER Smart Metering Project - Electricity Customer Behaviour Trial, 2009-2010 [dataset]. 1st Edition. Irish Social Science Data Archive. SN: 0012-00. https://www.ucd.ie/issda/data/commissionforenergyregulationcer/
