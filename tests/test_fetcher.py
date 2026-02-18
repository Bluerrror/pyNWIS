"""Tests for usgs_data_fetcher.fetcher module."""

import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from pynwis.fetcher import fetch_usgs_daily, usgs_json_to_df, fetch_batch_usgs_data


# --- Sample USGS JSON response for testing ---
SAMPLE_JSON = {
    "value": {
        "timeSeries": [
            {
                "sourceInfo": {
                    "siteCode": [{"value": "01491000"}]
                },
                "variable": {
                    "variableCode": [{"value": "00060"}]
                },
                "values": [
                    {
                        "value": [
                            {"dateTime": "2024-01-01T00:00:00.000", "value": "123.0"},
                            {"dateTime": "2024-01-02T00:00:00.000", "value": "456.0"},
                            {"dateTime": "2024-01-03T00:00:00.000", "value": ""},
                        ]
                    }
                ]
            }
        ]
    }
}

EMPTY_JSON = {"value": {"timeSeries": []}}


class TestUsgsJsonToDf:
    """Tests for usgs_json_to_df."""

    def test_valid_json(self):
        df = usgs_json_to_df(SAMPLE_JSON)
        assert not df.empty
        assert "site_no" in df.columns
        assert "time" in df.columns
        assert "00060" in df.columns
        assert len(df) == 3

    def test_values_parsed_correctly(self):
        df = usgs_json_to_df(SAMPLE_JSON)
        assert df.loc[0, "00060"] == 123.0
        assert df.loc[1, "00060"] == 456.0

    def test_empty_value_becomes_none(self):
        df = usgs_json_to_df(SAMPLE_JSON)
        assert pd.isna(df.loc[2, "00060"])

    def test_none_input(self):
        df = usgs_json_to_df(None)
        assert df.empty

    def test_empty_timeseries(self):
        df = usgs_json_to_df(EMPTY_JSON)
        assert df.empty

    def test_missing_value_key(self):
        df = usgs_json_to_df({"other": "data"})
        assert df.empty

    def test_time_column_is_datetime(self):
        df = usgs_json_to_df(SAMPLE_JSON)
        assert pd.api.types.is_datetime64_any_dtype(df["time"])


class TestFetchUsgsDaily:
    """Tests for fetch_usgs_daily."""

    @patch("pynwis.fetcher.requests.get")
    def test_successful_fetch(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_JSON
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = fetch_usgs_daily(
            sites=["01491000"],
            parameter_codes=["00060"],
            start="2024-01-01",
            end="2024-12-31",
        )
        assert result == SAMPLE_JSON
        mock_get.assert_called_once()

    @patch("pynwis.fetcher.requests.get")
    def test_returns_none_on_failure(self, mock_get):
        mock_get.side_effect = Exception("Network error")

        result = fetch_usgs_daily(
            sites=["01491000"],
            parameter_codes=["00060"],
            max_retries=1,
            pause=0,
        )
        assert result is None

    @patch("pynwis.fetcher.requests.get")
    def test_default_end_date_is_today(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_JSON
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from datetime import date

        fetch_usgs_daily(sites=["01491000"], parameter_codes=["00060"])
        call_url = mock_get.call_args[0][0]
        assert date.today().isoformat() in call_url


class TestFetchBatchUsgsData:
    """Tests for fetch_batch_usgs_data."""

    @patch("pynwis.fetcher.fetch_usgs_daily")
    def test_batch_returns_dataframe(self, mock_fetch):
        mock_fetch.return_value = SAMPLE_JSON

        df = fetch_batch_usgs_data(
            sites=["01491000"],
            parameter_codes=["00060"],
            start="2024-01-01",
            end="2024-12-31",
        )
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    @patch("pynwis.fetcher.fetch_usgs_daily")
    def test_batch_empty_when_no_data(self, mock_fetch):
        mock_fetch.return_value = None

        df = fetch_batch_usgs_data(
            sites=["99999999"],
            parameter_codes=["00060"],
            start="2024-01-01",
            end="2024-12-31",
        )
        assert df.empty

    @patch("pynwis.fetcher.fetch_usgs_daily")
    def test_required_params_filtering(self, mock_fetch):
        mock_fetch.return_value = SAMPLE_JSON

        df = fetch_batch_usgs_data(
            sites=["01491000"],
            parameter_codes=["00060", "80155"],
            required_params=["80155"],
            min_records=1,
            start="2024-01-01",
            end="2024-12-31",
        )
        # 80155 column will be all NaN, so site should be filtered out
        assert df.empty
