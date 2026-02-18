# example_usage.py
"""
Example Usage of pyNWIS
=======================

Demonstrates searching parameters, fetching data, and batch downloading.
"""

from pynwis import (
    get_usgs_parameters,
    search_parameters,
    fetch_usgs_daily,
    usgs_json_to_df,
    fetch_batch_usgs_data,
)

# Step 1: Browse and search the parameter catalog
params = get_usgs_parameters()
print(f"Available parameters: {len(params)}")
print(params[["parm_cd", "parameter_nm", "parameter_unit"]].head(10))

# Search for sediment-related parameters
sediment = search_parameters(params, "sediment")
print("\nSediment parameters:")
print(sediment[["parm_cd", "parameter_nm", "parameter_unit"]])

# Step 2: Fetch discharge data for a single site
print("\nFetching discharge for site 01491000...")
json_data = fetch_usgs_daily(
    sites=["01491000"],
    parameter_codes=["00060"],
    start="2024-01-01",
    end="2024-06-01",
)
df = usgs_json_to_df(json_data)
print(df.head())
print(f"Shape: {df.shape}")

# Step 3: Batch fetch for multiple sites with filtering
sites = ["01491000", "01646500"]
print(f"\nBatch fetching for {len(sites)} sites...")
data = fetch_batch_usgs_data(
    sites=sites,
    parameter_codes=["00060", "80154"],
    start="2020-01-01",
    required_params=["80154"],
    min_records=1,
)
print(f"Result shape: {data.shape}")
print(data.head())