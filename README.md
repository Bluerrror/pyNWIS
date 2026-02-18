# pyNWIS

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=180&color=0:0077b6,100:00b4d8&text=pyNWIS&fontColor=ffffff&fontSize=60&fontAlignY=35&desc=USGS%20Water%20Data%20for%20Python&descAlign=50&descAlignY=55" width="100%" alt="pyNWIS"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/pynwis/"><img src="https://img.shields.io/pypi/v/pynwis?color=00b4d8&style=for-the-badge" alt="PyPI"/></a>
  <a href="https://pypi.org/project/pynwis/"><img src="https://img.shields.io/pypi/pyversions/pynwis?style=for-the-badge&color=0077b6" alt="Python"/></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License"/></a>
</p>

<p align="center">
  A lightweight Python toolkit for downloading, processing, and filtering<br>
  <b>USGS National Water Information System (NWIS)</b> daily water data.
</p>

---

## ✨ Features

| Feature | Description |
|---|---|
| 📡 **Daily Value Fetching** | Download daily values from the USGS NWIS API with automatic retries and rate-limit handling |
| 📦 **Batch Downloads** | Fetch data for hundreds of sites at once with progress bars |
| 🧹 **Tidy DataFrames** | Convert raw JSON responses into clean Pandas DataFrames |
| 🔍 **Parameter Search** | Built-in catalog of 30+ common USGS parameter codes with keyword search |
| 🎯 **Smart Filtering** | Keep only sites with sufficient data for your required variables |

---

## 🚀 Installation

```bash
pip install pynwis
```

Or install from source:

```bash
git clone https://github.com/Bluerrror/pyNWIS.git
cd pyNWIS
pip install -e .
```

**Requirements:** Python ≥ 3.8 &nbsp;|&nbsp; `requests` &nbsp;|&nbsp; `pandas` &nbsp;|&nbsp; `tqdm`

---

## 📖 Quick Start

### 1. Fetch discharge data for a single site

```python
from pynwis import fetch_usgs_daily, usgs_json_to_df

json_data = fetch_usgs_daily(
    sites=["01491000"],
    parameter_codes=["00060"],       # Discharge (ft³/s)
    start="2024-01-01",
    end="2024-12-31",
)

df = usgs_json_to_df(json_data)
print(df.head())
#   site_no       time  00060
# 0  01491000 2024-01-01  222.0
# 1  01491000 2024-01-02  201.0
# 2  01491000 2024-01-03  187.0
```

### 2. Search the parameter catalog

```python
from pynwis import get_usgs_parameters, search_parameters

params = get_usgs_parameters()
print(params.head())
#   parm_cd     group                               parameter_nm parameter_unit
# 0   00010  Physical  Temperature, water, degrees Celsius          deg C
# 1   00020  Physical  Temperature, air, degrees Celsius            deg C

# Find sediment-related parameters
results = search_parameters(params, "sediment")
print(results[["parm_cd", "parameter_nm"]])
#   parm_cd                                      parameter_nm
# 0   80154       Suspended sediment concentration, mg/L
# 1   80155  Suspended sediment discharge, short tons per day
# 2   80225  Bedload sediment discharge, short tons per day
```

### 3. Batch download for multiple sites

```python
from pynwis import fetch_batch_usgs_data

sites = ["01491000", "01646500", "09522500"]

df = fetch_batch_usgs_data(
    sites=sites,
    parameter_codes=["00060"],            # Discharge
    start="2020-01-01",
)

print(df.shape)
print(df.head())
```

> **Tip:** Use `required_params=["80154"]` and `min_records=100` to keep only sites
> that have at least 100 suspended-sediment records.

---

## 📋 Common Parameter Codes

| Code | Name | Description | Units |
|------|------|-------------|-------|
| `00010` | Temperature | Water temperature | °C |
| `00060` | Discharge | Streamflow discharge | ft³/s |
| `00065` | Gage Height | Gage height | ft |
| `00045` | Precipitation | Precipitation depth | in |
| `00400` | pH | pH value | std units |
| `00300` | Dissolved O₂ | Dissolved oxygen | mg/L |
| `00630` | NO₃ + NO₂ | Nitrate plus nitrite | mg/L as N |
| `80154` | SSC | Suspended sediment concentration | mg/L |
| `80155` | SS Discharge | Suspended sediment discharge | tons/day |

> **Tip:** Call `get_usgs_parameters()` for the full built-in catalog, or use `search_parameters()` to find codes by keyword.

---

## 📚 API Reference

### Core Functions

| Function | Description |
|---|---|
| `fetch_usgs_daily(sites, parameter_codes, ...)` | Fetch raw NWIS daily-values JSON for one or more sites |
| `usgs_json_to_df(json_data)` | Convert NWIS JSON response into a tidy DataFrame |
| `fetch_batch_usgs_data(sites, parameter_codes, ...)` | Batch fetch with progress bars, retries, and filtering |

### Parameter Utilities

| Function | Description |
|---|---|
| `get_usgs_parameters()` | Return the built-in catalog of common parameter codes |
| `search_parameters(params_df, query, ...)` | Search parameters by keyword |

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m "Add amazing feature"`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built on the [USGS Water Services API](https://waterservices.usgs.gov).

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0077b6,100:00b4d8&height=100&section=footer"/>
