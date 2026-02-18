# pynwis/parameters.py
"""
USGS Parameter Codes Utilities
==============================

Functions to fetch and search USGS parameter codes dynamically.
"""

import requests
import pandas as pd
from typing import List, Optional, Union


def get_usgs_parameters() -> pd.DataFrame:
    """
    Fetch the complete list of USGS parameter codes from the official API.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: 'parm_cd' (str), 'group_cd' (str), 'parameter_nm' (str),
        and additional fields like units, CASRN, etc., if available in the RDB response.

    Notes
    -----
    Parses the tab-separated RDB format from USGS.
    Updates dynamically; no hardcoded list.
    """
    # Note: % encoded as %25 for URL
    url = "https://help.waterdata.usgs.gov/code/parameter_cd_query?fmt=rdb&group_cd=%25"

    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        lines = r.text.splitlines()
    except Exception as e:
        print(f"Failed to fetch parameter codes: {e}")
        return pd.DataFrame()

    # RDB format: Headers start with #, data follows
    headers = []
    data = []
    in_headers = True

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            if in_headers and line.startswith('#'):
                # Parse header for column names
                if 'tsv' in line.lower() or 'field' in line.lower():
                    parts = line.split('\t')
                    headers = [p.strip('# ').strip() for p in parts if p.strip()]
            continue
        else:
            in_headers = False
            parts = [p.strip() for p in line.split('\t')]
            if len(parts) >= 3:
                data.append(parts)

    if not data or not headers:
        print("No data parsed from USGS response.")
        return pd.DataFrame()

    # Map to known columns (adjust indices based on typical RDB)
    # Typical: parm_cd (0), group_cd (1), parameter_nm (2), etc.
    df_data = []
    for row in data:
        row_dict = {
            'parm_cd': row[0] if len(row) > 0 else '',
            'group_cd': row[1] if len(row) > 1 else '',
            'parameter_nm': row[2] if len(row) > 2 else '',
        }
        # Add more if headers allow, e.g., 'parameter_unit' at index 12 or so
        if len(headers) > 12 and 'parameter_unit' in headers:
            unit_idx = headers.index('parameter_unit')
            row_dict['parameter_unit'] = row[unit_idx] if len(row) > unit_idx else ''
        df_data.append(row_dict)

    df = pd.DataFrame(df_data)
    df = df[df['parm_cd'].str.isdigit()]  # Filter valid 5-digit codes
    df = df.sort_values('parm_cd').reset_index(drop=True)

    print(f"Fetched {len(df)} parameter codes.")
    return df


def search_parameters(
    params_df: pd.DataFrame,
    query: str,
    columns: List[str] = ['parameter_nm'],
    case_sensitive: bool = False
) -> pd.DataFrame:
    """
    Search for USGS parameters by keyword.

    Parameters
    ----------
    params_df : pd.DataFrame
        DataFrame from get_usgs_parameters().
    query : str
        Search term (e.g., 'discharge', 'sediment').
    columns : List[str], optional
        Columns to search in. Default: ['parameter_nm'].
    case_sensitive : bool, optional
        Whether to perform case-sensitive search. Default: False.

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame of matching parameters.
    """
    if params_df.empty:
        return params_df

    mask = pd.Series([False] * len(params_df))

    for col in columns:
        if col in params_df.columns:
            mask |= params_df[col].astype(str).str.contains(query, regex=False, case=case_sensitive, na=False)

    result = params_df[mask].copy()
    print(f"Found {len(result)} parameters matching '{query}'.")
    return result