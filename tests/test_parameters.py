"""Tests for pynwis.parameters module."""

import pandas as pd
import pytest
from pynwis.parameters import get_usgs_parameters, search_parameters


class TestGetUsgsParameters:
    """Tests for get_usgs_parameters."""

    def test_returns_dataframe(self):
        df = get_usgs_parameters()
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "parm_cd" in df.columns
        assert "parameter_nm" in df.columns
        assert "parameter_unit" in df.columns
        assert "group" in df.columns

    def test_contains_common_codes(self):
        df = get_usgs_parameters()
        codes = df["parm_cd"].tolist()
        assert "00060" in codes  # Discharge
        assert "00065" in codes  # Gage height
        assert "80154" in codes  # Suspended sediment concentration

    def test_sorted_by_parm_cd(self):
        df = get_usgs_parameters()
        assert df["parm_cd"].tolist() == sorted(df["parm_cd"].tolist())


class TestSearchParameters:
    """Tests for search_parameters."""

    def test_search_finds_matches(self):
        df = get_usgs_parameters()
        result = search_parameters(df, "discharge")
        assert len(result) >= 1
        assert any("ischarge" in nm for nm in result["parameter_nm"].tolist())

    def test_search_case_insensitive(self):
        df = get_usgs_parameters()
        result = search_parameters(df, "DISCHARGE")
        assert len(result) >= 1

    def test_search_no_matches(self):
        df = get_usgs_parameters()
        result = search_parameters(df, "nonexistent_param_xyz")
        assert len(result) == 0

    def test_search_empty_dataframe(self):
        df = pd.DataFrame()
        result = search_parameters(df, "discharge")
        assert result.empty

    def test_search_multiple_matches(self):
        df = get_usgs_parameters()
        result = search_parameters(df, "sediment")
        assert len(result) >= 2
