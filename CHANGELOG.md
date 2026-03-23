# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1] - 2026-03-23

### Changed
- Removed Python version from `.tool-versions` — Python version is managed solely by devcontainer
- Added `.devcontainer/aws-profile-map.json` to `.gitignore`
- Tags no longer use `v` prefix (e.g. `0.1.1` not `v0.1.1`)

### Fixed
- Removed sensitive file (`aws-profile-map.json`) from version control

## [0.1.0] - 2026-03-23

### Added
- `solark energy year` — retrieve monthly energy breakdown for an entire year
- `solark energy month` — retrieve daily energy breakdown for a specific month
- `solark energy day` — retrieve 5-minute interval energy data for a specific day
- `solark config show` — display all configuration values and their sources
- `--show-value` / `-V` flag for dollar value calculations with seasonal rate configuration
- `.env` file support for persistent configuration (23 configurable settings)
- JSON, CSV, and rich terminal table output formats
- DTE Energy R18 rate plan example rates (from actual bills)
- Structured logging with `--log-level` (debug, info, warning, error)
- Pre-push git hook enforcing lint, format check, and 90% test coverage
- 95 tests with 94% coverage
- Apache 2.0 license
