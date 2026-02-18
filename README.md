# pyNWIS

[![PyPI version](https://badge.fury.io/py/pynwis.svg)](https://badge.fury.io/py/pynwis)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/pynwis.svg)](https://pypi.org/project/pynwis/)

A Python package to fetch and process daily USGS National Water Information System (NWIS) data. Supports batch downloading across many sites and parameters, dynamic parameter code discovery, and filtering for data quality.

---

## Features

- **Dynamic Parameter Discovery** – Fetch and search all USGS parameter codes (e.g., discharge, sediment, temperature).
- **Batch Fetching** – Robust multi-site downloads with progress bars and retries.
- **Data Processing** – Convert NWIS JSON responses into tidy Pandas DataFrames.
- **Filtering Tools** – Keep only sites with sufficient data for desired variables.
- **Robust & Safe** – Handles rate limits, errors, and empty responses gracefully.

---

## Installation

```bash
pip install pynwis
```

Or install from source:

```bash
git clone https://github.com/Bluerrror/NWIS-Data-Downloader.git
cd NWIS-Data-Downloader
pip install -e .
```

**Requirements:** Python ≥ 3.8, plus `requests`, `pandas`, `tqdm`.

---

## Common Parameter Codes

Some frequently used USGS parameter codes (from USGS documentation):

| Parameter Code | Short Name         | Description                       | Units      |
|----------------|--------------------|-----------------------------------|------------|
| 00010          | Temperature        | Water temperature                 | °C         |
| 00060          | Discharge          | Streamflow discharge              | ft³/s      |
| 00065          | Gage Height        | Gage height                       | ft         |
| 00045          | Precipitation      | Precipitation depth               | in         |
| 00400          | pH                 | pH value                          | unitless   |
| 00630          | Nitrate            | Nitrogen, nitrate                 | mg/L as N  |
| 00631          | Nitrate + Nitrite  | Nitrate plus nitrite              | mg/L as N  |
| 80155          | Suspended Sediment | Suspended sediment concentration  | mg/L       |

For a complete list, call:

```python
get_usgs_parameters()
```

---

## Quickstart

### 1. Discover and Search Parameters

```python
from pynwis import get_usgs_parameters, search_parameters

params_df = get_usgs_parameters()
print(f"Total parameters: {len(params_df)}")

# Search for discharge-related parameters
discharge_params = search_parameters(params_df, 'discharge')
print(discharge_params[['parm_cd', 'parameter_nm', 'parameter_unit']].head())

# Example: search for temperature or pH
wq_params = search_parameters(params_df, 'temperature OR pH', columns=['parameter_nm'])
print(f"Water Quality Matches: {len(wq_params)}")
```

---

### 2. Fetch Data for a Single Site

```python
from pynwis import fetch_usgs_daily, usgs_json_to_df

site = '01491000'
json_data = fetch_usgs_daily(
    sites=[site],
    parameter_codes=['00060'],  # Discharge
    start='2024-01-01',
    end='2025-01-01'
)

df = usgs_json_to_df(json_data)
print(df.head())
print(df.shape)
```

---

### 3. Batch Fetch with Filtering

```python
from pynwis import fetch_batch_usgs_data

sites = [
    '01491000',
    '01646500',
    '09522500'
]

selected_codes = ['00060', '80155']  # Discharge + Suspended Sediment

data_df = fetch_batch_usgs_data(
    sites=sites,
    parameter_codes=selected_codes,
    start='2000-01-01',
    end='2025-01-01',
    required_params=['80155'],
    min_records=100,
    batch_size=10
)

print(data_df.shape)
print(data_df.describe())
```

---

### 4. Interactive Parameter Selection

```python
import pandas as pd
from pynwis import get_usgs_parameters, search_parameters

params_df = get_usgs_parameters()
query = input("Enter search term (e.g., 'sediment'): ").strip()
matches = search_parameters(params_df, query)

if not matches.empty:
    print(matches[['parm_cd', 'parameter_nm']].to_string(index=False))
    codes = input("Enter comma-separated codes (or 'all'): ").strip()
    selected_codes = matches['parm_cd'].tolist() if codes.lower() == 'all' else [c.strip() for c in codes.split(',')]
    print(f"Selected: {selected_codes}")
else:
    print("No matches found.")
    selected_codes = ['00060']  # Default
```

---

### 5. Save & Visualize Data

```python
import matplotlib.pyplot as plt

data_df.to_csv('usgs_hydrology_data.csv', index=False)

data_df['time'] = pd.to_datetime(data_df['time'])
plt.figure(figsize=(12, 6))

for site in data_df['site_no'].unique()[:2]:
    site_data = data_df[data_df['site_no'] == site]
    plt.plot(site_data['time'], site_data['00060'], label=f'Site {site}')

plt.xlabel('Date')
plt.ylabel('Discharge (cfs)')
plt.title('Daily Streamflow Trends')
plt.legend()
plt.savefig('discharge_plot.png')
plt.show()
```


---

## API Reference

### Core Functions

- `fetch_usgs_daily(sites, parameter_codes, ...)` — Fetch raw NWIS daily JSON data.
- `usgs_json_to_df(json_data)` — Convert JSON to tidy DataFrame.
- `fetch_batch_usgs_data(sites, parameter_codes, ...)` — Multi-site batch fetch with filtering.

### Parameter Utilities

- `get_usgs_parameters()` — Download complete parameter catalog.
- `search_parameters(params_df, query, ...)` — Query parameters by keyword.

Full documentation can be found in `pynwis/fetcher.py` and `pynwis/parameters.py`.

---

## Examples

- **Water Quality Batch**: Use `['00010', '00400']` for temperature + pH.
- **Precipitation Analysis**: Use `['00045']` for precipitation depth.
- **Large-Scale Fetching**: Set `batch_size=200` for thousands of sites.
- **Error Handling**: Wrap fetches in `try/except` for production pipelines.

---

## Contributing

1. Fork the repo
2. Create a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Commit changes:
   ```bash
   git commit -m "Add amazing feature"
   ```
4. Push:
   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request

---

## License

MIT License — see `LICENSE` for details.

---

## Acknowledgments

Built on the excellent USGS NWIS API:  
https://waterservices.usgs.gov
