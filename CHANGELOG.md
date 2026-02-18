# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-02-18

### Fixed
- `get_usgs_parameters()` — replaced broken USGS RDB endpoint with built-in catalog of 30+ common parameter codes
- Removed `requests` dependency from `parameters.py` (no longer needed for parameter lookup)

### Changed
- Rewrote README with beautiful formatting, working examples, and verified output
- Updated `example_usage.py` with working examples

## [0.1.0] - 2024-12-12

### Added
- Initial release
- `fetch_usgs_daily` — Fetch raw NWIS daily JSON data with retry and rate-limit handling
- `usgs_json_to_df` — Convert USGS JSON responses into tidy Pandas DataFrames
- `fetch_batch_usgs_data` — Multi-site batch fetch with progress bars and filtering
- `get_usgs_parameters` — Dynamic USGS parameter code discovery
- `search_parameters` — Keyword search across parameter catalogs
- PyPI publishing workflow
- Example usage script
