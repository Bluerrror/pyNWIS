# pynwis/fetcher.py
"""
USGS Data Fetcher - Core Functions
==================================

Functions to fetch and process USGS daily values data.
"""

import requests
import pandas as pd
import time
from datetime import date
from typing import List, Optional, Dict, Any
from tqdm import tqdm


def fetch_usgs_daily(
    sites: List[str],
    parameter_codes: List[str],
    start: str = "1900-01-01",
    end: Optional[str] = None,
    max_retries: int = 5,
    pause: int = 1
) -> Optional[Dict[str, Any]]:
    """
    Fetch daily USGS NWIS data for multiple sites and parameters.

    Parameters
    ----------
    sites : List[str]
        List of 8-digit USGS site IDs.
    parameter_codes : List[str]
        List of 5-digit USGS parameter codes (e.g., ['00060', '80155']).
    start : str, optional
        Start date in YYYY-MM-DD format. Default: "1900-01-01".
    end : str, optional
        End date in YYYY-MM-DD format. Default: today's date.
    max_retries : int, optional
        Maximum number of retry attempts on failure. Default: 5.
    pause : int, optional
        Base pause time (seconds) between retries. Default: 1.

    Returns
    -------
    Optional[Dict[str, Any]]
        JSON response from USGS API, or None on failure.

    Notes
    -----
    Handles rate limiting (HTTP 429) with exponential backoff.
    """
    if end is None:
        end = date.today().isoformat()

    site_str = ",".join(sites)
    param_str = ",".join(parameter_codes)

    url = (
        "https://waterservices.usgs.gov/nwis/dv/"
        f"?format=json&sites={site_str}"
        f"&parameterCd={param_str}"
        f"&startDT={start}&endDT={end}"
        "&siteStatus=all"
    )

    for attempt in range(max_retries):
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 429:
                # Too many requests → backoff
                time.sleep(pause * (2 ** attempt))  # Exponential backoff
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(pause * (2 ** attempt))

    print("Failed to fetch data after all retries.")
    return None


def usgs_json_to_df(json_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert USGS JSON daily values to a tidy Pandas DataFrame.

    Parameters
    ----------
    json_data : Dict[str, Any]
        JSON response from USGS API.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: 'site_no', 'time', and one column per parameter code.
        Rows are unique site-time combinations; values are floats or NaN.

    Notes
    -----
    Assumes the first value block contains the data (daily values).
    Handles empty values as NaN.
    """
    if (json_data is None) or ("value" not in json_data):
        return pd.DataFrame()

    records = []
    time_series = json_data["value"].get("timeSeries", [])
    if not time_series:
        return pd.DataFrame()

    for site in time_series:
        site_no = site["sourceInfo"]["siteCode"][0]["value"]
        var_code = site["variable"]["variableCode"][0]["value"]

        values = site["values"][0].get("value", [])
        for entry in values:
            record = {
                "site_no": site_no,
                "time": entry["dateTime"],
                var_code: float(entry["value"]) if entry["value"] != "" else None
            }
            records.append(record)

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    # Pivot to ensure one row per site-time, taking first value if duplicates
    df = df.groupby(["site_no", "time"]).agg("first").reset_index()
    df["time"] = pd.to_datetime(df["time"])

    return df


def fetch_batch_usgs_data(
    sites: List[str],
    parameter_codes: List[str],
    start: str = "1900-01-01",
    end: Optional[str] = None,
    required_params: Optional[List[str]] = None,
    min_records: int = 1,
    batch_size: int = 50,
    **kwargs
) -> pd.DataFrame:
    """
    Batch fetch USGS daily data for a list of sites, with progress tracking.

    Parameters
    ----------
    sites : List[str]
        List of 8-digit USGS site IDs to fetch data for.
    parameter_codes : List[str]
        List of 5-digit USGS parameter codes.
    start : str, optional
        Start date. Default: "1900-01-01".
    end : str, optional
        End date. Default: today's date.
    required_params : Optional[List[str]], optional
        Subset of parameter_codes; only keep sites with at least min_records non-NA values
        for ANY of these params. If None, keep all sites with any data. Default: None.
    min_records : int, optional
        Minimum number of valid records required for a site to be kept. Default: 1.
    batch_size : int, optional
        Number of sites per batch (to avoid URL length limits). Default: 50.
    **kwargs
        Additional args passed to fetch_usgs_daily.

    Returns
    -------
    pd.DataFrame
        Combined DataFrame of all valid site data.

    Notes
    -----
    Fetches in batches to handle large site lists.
    Filters sites based on required_params if specified.
    Uses tqdm for progress visualization.
    """
    if required_params is None:
        required_params = []

    if end is None:
        end = date.today().isoformat()

    all_data = []
    success_count = 0
    valid_site_count = 0

    # Process in batches
    for i in range(0, len(sites), batch_size):
        batch_sites = sites[i:i + batch_size]
        pbar = tqdm(total=len(batch_sites), desc=f"Batch {i//batch_size + 1}", leave=False, ncols=120)

        batch_data = []
        for site in batch_sites:
            pbar.set_postfix({"site": site, "success": success_count, "valid": valid_site_count})

            json_data = fetch_usgs_daily(
                sites=[site],
                parameter_codes=parameter_codes,
                start=start,
                end=end,
                **kwargs
            )

            df = usgs_json_to_df(json_data)

            # Ensure all expected columns
            expected_cols = ["site_no", "time"] + parameter_codes
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = None

            df = df[expected_cols]

            if not df.empty:
                batch_data.append(df)
                success_count += 1

            pbar.update(1)

        pbar.close()

        # Combine batch
        if batch_data:
            batch_df = pd.concat(batch_data, ignore_index=True)

            # Filter if required_params specified: keep sites with >= min_records for ANY required param
            if required_params:
                valid_sites = set()
                for param in required_params:
                    if param in batch_df.columns:
                        site_counts = batch_df.groupby('site_no')[param].apply(lambda x: x.notna().sum())
                        valid_sites.update(site_counts[site_counts >= min_records].index.tolist())
                if valid_sites:
                    batch_df = batch_df[batch_df['site_no'].isin(valid_sites)]
                else:
                    batch_df = pd.DataFrame(columns=batch_df.columns)  # Empty if no valid sites

            if not batch_df.empty:
                all_data.append(batch_df)
                valid_site_count += len(batch_df["site_no"].unique())

    expected_cols = ["site_no", "time"] + parameter_codes

    if not all_data:
        return pd.DataFrame(columns=expected_cols)

    full_dataset = pd.concat(all_data, ignore_index=True)
    full_dataset = full_dataset.dropna(how='all')  # Drop fully empty rows

    print(f"\nCombined dataset shape: {full_dataset.shape}")
    print("Columns:", full_dataset.columns.tolist())

    return full_dataset