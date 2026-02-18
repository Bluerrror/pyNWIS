"""Tests for usgs_data_fetcher.parameters module."""

import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from pynwis.parameters import get_usgs_parameters, search_parameters


# Sample RDB-style response from USGS (matching real USGS format)
SAMPLE_RDB_RESPONSE = """#
# US Geological Survey
# retrieved: 2024-01-01
# field\tparm_cd\tgroup_cd\tparameter_nm\tparameter_units\tcasrn\tsrsname\tparameter_fld\tparameter_lab\tparameter_type\tparameter_source\tparameter_class\tparameter_description\tparameter_unit
parm_cd\tgroup_cd\tparameter_nm\tparameter_units\tcasrn\tsrsname\tparameter_fld\tparameter_lab\tparameter_type\tparameter_source\tparameter_class\tparameter_description\tparameter_unit
5s\t7s\t170s\t60s\t12s\t60s\t60s\t60s\t7s\t7s\t7s\t500s\t12s
00060\tPhysical\tDischarge, cubic feet per second\tft3/s\t\tStreamflow\t\t\t\t\t\t\tft3/s
00065\tPhysical\tGage height, feet\tft\t\tGage height\t\t\t\t\t\t\tft
80155\tSediment\tSuspended sediment concentration, milligrams per liter\tmg/l\t\tSSC\t\t\t\t\t\t\tmg/l
00010\tPhysical\tTemperature, water, degrees Celsius\tdeg C\t\tTemperature\t\t\t\t\t\t\tdeg C
"""


class TestGetUsgsParameters:
    """Tests for get_usgs_parameters."""

    @patch("pynwis.parameters.requests.get")
    def test_returns_dataframe(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SAMPLE_RDB_RESPONSE
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        df = get_usgs_parameters()
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "parm_cd" in df.columns
        assert "parameter_nm" in df.columns

    @patch("pynwis.parameters.requests.get")
    def test_returns_empty_on_failure(self, mock_get):
        mock_get.side_effect = Exception("Connection error")
        df = get_usgs_parameters()
        assert df.empty


class TestSearchParameters:
    """Tests for search_parameters."""

    def _make_params_df(self):
        return pd.DataFrame({
            "parm_cd": ["00060", "00065", "80155", "00010"],
            "parameter_nm": [
                "Discharge, cubic feet per second",
                "Gage height, feet",
                "Suspended sediment concentration",
                "Temperature, water",
            ],
        })

    def test_search_finds_matches(self):
        df = self._make_params_df()
        result = search_parameters(df, "discharge")
        assert len(result) == 1
        assert result.iloc[0]["parm_cd"] == "00060"

    def test_search_case_insensitive(self):
        df = self._make_params_df()
        result = search_parameters(df, "DISCHARGE")
        assert len(result) == 1

    def test_search_no_matches(self):
        df = self._make_params_df()
        result = search_parameters(df, "nonexistent_param_xyz")
        assert len(result) == 0

    def test_search_empty_dataframe(self):
        df = pd.DataFrame()
        result = search_parameters(df, "discharge")
        assert result.empty

    def test_search_multiple_matches(self):
        df = self._make_params_df()
        result = search_parameters(df, "e")  # matches multiple
        assert len(result) >= 2
