# solark-cloud-cli

> **⚠️ WARNING: This project is currently in testing. The `main` branch is not considered stable. Only tagged releases (e.g. `0.2.0`) are intended for use. Expect breaking changes until a stable release is published.**

CLI tool for retrieving solar energy production data from [Sol-Ark](https://sol-ark.com/) inverter systems via the SolarkCloud API.

## Features

- Retrieve yearly, monthly, and daily energy data from the SolarkCloud monitoring platform
- Dollar value calculations with configurable utility rate structures (seasonal + time-of-use)
- Output in JSON, CSV, or rich terminal table format
- `.env` file support for persistent configuration
- Fully configurable via environment variables or CLI arguments
- Hierarchical, self-documenting command help at every level
- Structured logging with configurable verbosity

## Installation

Requires Python 3.12+.

### With pipx (recommended)

```bash
pipx install git+https://github.com/matthew-dresden/solark-cloud-cli.git@0.2.0
```

### From source

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/matthew-dresden/solark-cloud-cli.git
cd solark-cloud-cli
make dev
```

## Quick Start

1. Copy the example config and fill in your credentials:

```bash
cp .env.example .env
# Edit .env with your SolarkCloud credentials
```

2. Retrieve your 2025 energy data:

```bash
solark energy year --date 2025
```

3. See dollar values with rate configuration:

```bash
solark energy year --date 2025 --show-value
```

## Configuration

All configuration is driven by a `.env` file, environment variables, or CLI arguments. Precedence: **CLI flag > environment variable > .env file > default**.

### Account Settings

| Environment Variable | CLI Flag | Description | Default |
|---------------------|----------|-------------|---------|
| `SOLARK_USERNAME` | `--username`, `-u` | SolarkCloud account email | *(required)* |
| `SOLARK_PASSWORD` | `--password`, `-p` | SolarkCloud account password | *(required)* |
| `SOLARK_PLANT_ID` | `--plant-id` | Plant ID (from your SolarkCloud URL) | *(required)* |
| `SOLARK_API_URL` | | API base URL | `https://api.solarkcloud.com` |
| `SOLARK_OUTPUT_FORMAT` | `--output-format`, `-o` | Output format: `json`, `csv`, `table` | `table` |
| `SOLARK_TIMEOUT` | | HTTP request timeout in seconds | `30` |
| `SOLARK_LOG_LEVEL` | `--log-level`, `-l` | Log verbosity: `debug`, `info`, `warning`, `error` | `warning` |

### Rate Configuration (for `--show-value`)

These settings enable dollar value calculations. They work with any utility — set the rates from your own electric bill. The `.env.example` includes DTE Energy rates as a working example.

**Season boundaries:**

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `SOLARK_RATE_SUMMER_START` | Summer season start (MM-DD) | `06-01` |
| `SOLARK_RATE_SUMMER_END` | Summer season end (MM-DD) | `09-30` |

**Blended average rates ($/kWh)** — used for yearly and monthly value calculations:

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `SOLARK_RATE_SUMMER_INFLOW` | Summer avoided retail rate | *(required for --show-value)* |
| `SOLARK_RATE_SUMMER_OUTFLOW` | Summer export credit rate | *(required for --show-value)* |
| `SOLARK_RATE_NONSUMMER_INFLOW` | Non-summer avoided retail rate | *(required for --show-value)* |
| `SOLARK_RATE_NONSUMMER_OUTFLOW` | Non-summer export credit rate | *(required for --show-value)* |

**Time-of-use peak period:**

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `SOLARK_RATE_PEAK_START` | Peak period start (HH:MM) | `15:00` |
| `SOLARK_RATE_PEAK_END` | Peak period end (HH:MM) | `19:00` |
| `SOLARK_RATE_PEAK_DAYS` | Peak days (comma-separated) | `mon,tue,wed,thu,fri` |

**Granular TOU rates ($/kWh)** — on-peak and off-peak by season:

| Environment Variable | Description |
|---------------------|-------------|
| `SOLARK_RATE_SUMMER_PEAK_INFLOW` | Summer on-peak inflow rate |
| `SOLARK_RATE_SUMMER_OFFPEAK_INFLOW` | Summer off-peak inflow rate |
| `SOLARK_RATE_SUMMER_PEAK_OUTFLOW` | Summer on-peak outflow credit |
| `SOLARK_RATE_SUMMER_OFFPEAK_OUTFLOW` | Summer off-peak outflow credit |
| `SOLARK_RATE_NONSUMMER_PEAK_INFLOW` | Non-summer on-peak inflow rate |
| `SOLARK_RATE_NONSUMMER_OFFPEAK_INFLOW` | Non-summer off-peak inflow rate |
| `SOLARK_RATE_NONSUMMER_PEAK_OUTFLOW` | Non-summer on-peak outflow credit |
| `SOLARK_RATE_NONSUMMER_OFFPEAK_OUTFLOW` | Non-summer off-peak outflow credit |

### Finding Your Plant ID

Your plant ID is in your SolarkCloud URL: `https://www.solarkcloud.com/plants/overview/{PLANT_ID}/...`

### Understanding Rate Configuration

The value calculation uses two components:

1. **Avoided retail cost** — energy self-consumed from solar/battery instead of purchasing from the grid, valued at the inflow rate
2. **Export credit** — excess energy exported to the grid, credited at the outflow rate

The formula per time period: `Value = (Load - Import) × inflow_rate + Export × outflow_rate`

Rates vary by season (summer vs. non-summer). Set the blended average rates in your `.env` file based on your utility rate plan. The blended rate is the effective all-in cost per kWh from your actual bills (total charges divided by total kWh).

### Example: DTE Energy R18 Rate Plan

The `.env.example` file is pre-populated with rates from DTE Energy rate plan **R18 Cat1 TOD 3PM-7PM** (Rider 18 Distributed Generation with Time-of-Day pricing). These rates were extracted from actual DTE bills.

**Rate sources:**
- Summer rates: DTE bill Jul 14, 2025 (service Jun 12 - Jul 11, 2025)
- Non-summer rates: DTE bill Mar 12, 2026 (service Feb 10 - Mar 11, 2026, post-MPSC March 5, 2026 rate change)

**DTE season definition:** Summer is June 1 through September 30. Non-summer is October 1 through May 31.

**DTE TOU peak period:** 3:00 PM - 7:00 PM, weekdays only.

**Inflow rate components (what you pay per kWh imported):**

| Component | Summer On-Peak | Summer Off-Peak | Non-Summer On-Peak | Non-Summer Off-Peak |
|-----------|---------------:|----------------:|-------------------:|--------------------:|
| Capacity | $0.05649 | $0.03403 | $0.03839 | $0.03240 |
| Non-Capacity | $0.08838 | $0.05325 | $0.06480 | $0.05469 |
| PSCR | $0.00250 | $0.00250 | $0.01877 | $0.01877 |
| Distribution | $0.08907 | $0.08907 | $0.09726 | $0.09726 |
| **Total** | **$0.23644** | **$0.17885** | **$0.21922** | **$0.20312** |

**Outflow credit rates (what you earn per kWh exported):**

| Season | On-Peak | Off-Peak |
|--------|--------:|---------:|
| Summer | $0.14737 | $0.08978 |
| Non-Summer | $0.12196 | $0.10586 |

**Blended rates (effective all-in from actual bills):**

| Season | Inflow ($/kWh) | Outflow ($/kWh) | Source |
|--------|---------------:|----------------:|--------|
| Summer | $0.2235 | $0.1038 | $87.39 / 390.879 kWh; $141.65 / 1364.273 kWh |
| Non-Summer | $0.2274 | $0.0990 | $243.61 / 1071.513 kWh; $118.17 / 1193.838 kWh |

To use these rates, copy `.env.example` to `.env` — the DTE R18 rates are already filled in. If you're on a different utility or rate plan, replace with your own rates.

## Usage

### Energy Data Commands

```bash
# Yearly data (monthly breakdown)
solark energy year --date 2025

# Monthly data (daily breakdown)
solark energy month --date 2025-04

# Monthly aggregate (single-row summary for one month)
solark energy month --date 2025-07 --summary

# Daily data (5-minute intervals, values in watts)
solark energy day --date 2025-04-15
```

### Dollar Value Calculations

Add `--show-value` / `-V` to see dollar value columns (requires rate configuration):

```bash
# Year with values — shows Self-Used, Avoided $, Export $, Value $ columns
solark energy year --date 2025 --show-value

# Single month summary with values
solark energy month --date 2025-07 --summary --show-value

# Month daily breakdown with values
solark energy month --date 2025-07 --show-value
```

Value calculations are available for `year` and `month` (including `--summary`) commands where data is in kWh. The `day` command returns data in watts and does not support value calculations.

### Output Formats

```bash
# Rich terminal table (default)
solark energy year --date 2025

# JSON
solark energy year --date 2025 --output-format json

# CSV
solark energy year --date 2025 --output-format csv

# CSV with values (pivoted format)
solark energy year --date 2025 --show-value --output-format csv
```

### Logging

```bash
# Default (warnings only)
solark energy year --date 2025

# Info level — shows authentication and API request details
solark energy year --date 2025 --log-level info

# Debug level — shows full request/response details
solark energy year --date 2025 --log-level debug

# Via environment variable
SOLARK_LOG_LEVEL=debug solark energy year --date 2025
```

### Inline Credentials

```bash
solark energy year --date 2025 --plant-id 125647 --username user@example.com --password mypass
```

### View Configuration

```bash
solark config show
```

### Help at Any Level

```bash
solark --help
solark energy --help
solark energy year --help
solark config --help
```

## Data Labels

Energy endpoints return these metrics (all in kWh for year/month, watts for day):

| Label | Description |
|-------|-------------|
| PV | Solar panel production |
| Load | Total home consumption |
| Export | Energy sent to the grid |
| Import | Energy purchased from the grid |
| Charge | Energy stored in batteries |
| Discharge | Energy released from batteries |

## Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- make

### Setup

```bash
make dev
```

### Available Make Targets

```
make help            Show all available targets
make install         Install production dependencies
make dev             Install with dev dependencies
make test            Run tests
make lint            Lint code with ruff
make format          Format code with ruff
make format-check    Check formatting without modifying files
make coverage        Run tests with coverage report
make pre-push-check  Run all validation checks (lint + format + tests)
make clean           Remove build artifacts and cache
make run             Run the CLI (pass args via ARGS="...")
```

### Running Tests

```bash
make test             # Run all tests
make coverage         # Run with coverage report
```

### Pre-push Hooks

A git pre-push hook runs `make pre-push-check` automatically before every push, which runs lint, format check, and tests with 90% coverage enforcement.

### Project Structure

```
src/solark_cloud_cli/
├── main.py              # Typer app entry point, logging setup
├── config.py            # pydantic-settings configuration (.env + env vars)
├── commands/            # CLI subcommands (energy, config)
├── client/              # HTTP client, auth, URL building
├── services/            # Business logic (energy, valuation, config display)
├── models/              # Pydantic models (API + domain)
└── formatters/          # Output formatting (JSON, CSV, table)
```

### Architecture

The project follows SOLID principles with clear separation of concerns:

- **CLI layer** (`commands/`) — argument parsing and output display
- **Service layer** (`services/`) — business logic, data transformation, valuation
- **Client layer** (`client/`) — HTTP communication and authentication
- **Models** (`models/`) — API response models and domain models
- **Formatters** (`formatters/`) — pluggable output formatting via Protocol

## API Notes

The SolarkCloud API is not officially documented. The endpoints used by this tool were confirmed through testing and community research. The API may change without notice.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
