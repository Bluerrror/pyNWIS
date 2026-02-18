# pynwis/parameters.py
"""
USGS Parameter Codes Utilities
==============================

Built-in catalog of common USGS NWIS parameter codes and search utilities.
"""

import pandas as pd
from typing import List


# Comprehensive built-in catalog of commonly used USGS parameter codes
_PARAMETER_CATALOG = [
    ("00010", "Physical", "Temperature, water, degrees Celsius", "deg C"),
    ("00020", "Physical", "Temperature, air, degrees Celsius", "deg C"),
    ("00045", "Physical", "Precipitation, total, inches", "in"),
    ("00060", "Physical", "Discharge, cubic feet per second", "ft3/s"),
    ("00065", "Physical", "Gage height, feet", "ft"),
    ("00095", "Physical", "Specific conductance, water, unfiltered, uS/cm at 25C", "uS/cm"),
    ("00300", "Physical", "Dissolved oxygen, water, unfiltered, mg/L", "mg/L"),
    ("00400", "Physical", "pH, water, unfiltered, field, standard units", "std units"),
    ("00410", "Physical", "Acid neutralizing capacity, water, unfiltered, mg/L as CaCO3", "mg/L"),
    ("00480", "Sediment", "Salinity, water, unfiltered, parts per thousand", "ppt"),
    ("00530", "Sediment", "Suspended solids, water, unfiltered, mg/L", "mg/L"),
    ("00600", "Nutrient", "Total nitrogen, water, unfiltered, mg/L", "mg/L"),
    ("00605", "Nutrient", "Organic nitrogen, water, unfiltered, mg/L", "mg/L"),
    ("00608", "Nutrient", "Ammonia, water, filtered, mg/L as N", "mg/L"),
    ("00613", "Nutrient", "Nitrite, water, filtered, mg/L as N", "mg/L"),
    ("00618", "Nutrient", "Nitrate, water, filtered, mg/L as N", "mg/L"),
    ("00625", "Nutrient", "Ammonia plus organic nitrogen, water, unfiltered, mg/L as N", "mg/L"),
    ("00630", "Nutrient", "Nitrate plus nitrite, water, unfiltered, mg/L as N", "mg/L"),
    ("00631", "Nutrient", "Nitrate plus nitrite, water, filtered, mg/L as N", "mg/L"),
    ("00665", "Nutrient", "Phosphorus, water, unfiltered, mg/L as P", "mg/L"),
    ("00680", "Nutrient", "Organic carbon, water, unfiltered, mg/L", "mg/L"),
    ("00681", "Nutrient", "Organic carbon, water, filtered, mg/L", "mg/L"),
    ("70331", "Physical", "Suspended sediment, sieve diameter, percent finer than 0.0625 mm", "%"),
    ("72019", "Physical", "Depth to water level, feet below land surface", "ft"),
    ("72020", "Physical", "Elevation above NGVD 1929, feet", "ft"),
    ("80154", "Sediment", "Suspended sediment concentration, mg/L", "mg/L"),
    ("80155", "Sediment", "Suspended sediment discharge, short tons per day", "tons/day"),
    ("80225", "Sediment", "Bedload sediment discharge, short tons per day", "tons/day"),
    ("99133", "Nutrient", "Nitrate plus nitrite, water, in situ, mg/L as N", "mg/L"),
    ("63680", "Physical", "Turbidity, water, unfiltered, FNU", "FNU"),
]


def get_usgs_parameters() -> pd.DataFrame:
    """
    Return the built-in catalog of common USGS NWIS parameter codes.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: ``parm_cd``, ``group``, ``parameter_nm``,
        ``parameter_unit``.

    Examples
    --------
    >>> from pynwis import get_usgs_parameters
    >>> params = get_usgs_parameters()
    >>> params.head(3)
      parm_cd     group                              parameter_nm parameter_unit
    0   00010  Physical  Temperature, water, degrees Celsius          deg C
    """
    df = pd.DataFrame(
        _PARAMETER_CATALOG,
        columns=["parm_cd", "group", "parameter_nm", "parameter_unit"],
    )
    df = df.sort_values("parm_cd").reset_index(drop=True)
    return df


def search_parameters(
    params_df: pd.DataFrame,
    query: str,
    columns: List[str] = ["parameter_nm"],
    case_sensitive: bool = False,
) -> pd.DataFrame:
    """
    Search for USGS parameters by keyword.

    Parameters
    ----------
    params_df : pd.DataFrame
        DataFrame from :func:`get_usgs_parameters`.
    query : str
        Search term (e.g., ``'discharge'``, ``'sediment'``).
    columns : list of str, optional
        Columns to search in. Default: ``['parameter_nm']``.
    case_sensitive : bool, optional
        Whether to perform case-sensitive search. Default: ``False``.

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame of matching parameters.

    Examples
    --------
    >>> from pynwis import get_usgs_parameters, search_parameters
    >>> params = get_usgs_parameters()
    >>> search_parameters(params, 'discharge')
      parm_cd     group                              parameter_nm parameter_unit
    ...
    """
    if params_df.empty:
        return params_df

    mask = pd.Series([False] * len(params_df))

    for col in columns:
        if col in params_df.columns:
            mask |= params_df[col].astype(str).str.contains(
                query, regex=False, case=case_sensitive, na=False
            )

    return params_df[mask].copy().reset_index(drop=True)