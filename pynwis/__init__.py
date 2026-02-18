# pynwis/__init__.py
"""
pyNWIS
======

A Python package to fetch and process daily USGS NWIS data for multiple sites and parameters.
Includes utilities to discover and select parameter codes dynamically.

Key Features:
- Fetch daily values from USGS NWIS API.
- Convert JSON responses to tidy Pandas DataFrames.
- Batch fetch for multiple sites with progress tracking.
- Dynamic retrieval of USGS parameter codes for easy selection.

Installation:
pip install pynwis

Usage:
from pynwis import fetch_batch_usgs_data, get_usgs_parameters, search_parameters

# Get parameter info
params_df = get_usgs_parameters()
sediment_params = search_parameters(params_df, 'sediment')

# Fetch data
sites = ['12345678', '87654321']  # List of 8-digit site IDs
data_df = fetch_batch_usgs_data(sites, ['00060', '80155'])
"""

from .fetcher import (
    fetch_usgs_daily,
    usgs_json_to_df,
    fetch_batch_usgs_data
)
from .parameters import (
    get_usgs_parameters,
    search_parameters
)

__version__ = '0.1.1'
__all__ = [
    'fetch_usgs_daily',
    'usgs_json_to_df',
    'fetch_batch_usgs_data',
    'get_usgs_parameters',
    'search_parameters'
]