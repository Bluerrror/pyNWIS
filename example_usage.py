# example_usage.py
"""
Example Usage of USGS Data Fetcher Package
==========================================

Demonstrates fetching parameter info, selecting codes, and batch downloading data.
"""

import pandas as pd
from pynwis import (
    get_usgs_parameters,
    search_parameters,
    fetch_batch_usgs_data
)

# Step 1: Fetch all parameter codes
print("Fetching USGS parameter codes...")
params_df = get_usgs_parameters()

# Step 2: Search and select parameters (example: discharge and suspended sediment)
discharge_params = search_parameters(params_df, 'discharge')
print("\nDischarge parameters:")
print(discharge_params[['parm_cd', 'parameter_nm', 'parameter_unit']])

sediment_params = search_parameters(params_df, 'suspended sediment')
print("\nSuspended sediment parameters:")
print(sediment_params[['parm_cd', 'parameter_nm', 'parameter_unit']])

# Select specific codes (user would choose here)
selected_codes = ['00060', '80155']  # Discharge (cfs), Suspended sediment load (mg/l)

# Step 3: Define sites (example: replace with your list or from df['Gage_no'])
sites = ['01491000', '01646500']  # Example USGS sites (Delaware River, Susquehanna River)

# Step 4: Batch fetch data, keeping only sites with sediment data
print("\nFetching data...")
data_df = fetch_batch_usgs_data(
    sites=sites,
    parameter_codes=selected_codes,
    required_params=['80155'],  # Keep sites with >0 sediment records
    min_records=1
)

print("\nFinal dataset:")
print(data_df.head())
print(f"Shape: {data_df.shape}")

# Save if needed
# data_df.to_csv('usgs_data.csv', index=False)