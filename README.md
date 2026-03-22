# solark-cloud-cli

CLI tool for retrieving solar energy production data from [Sol-Ark](https://sol-ark.com/) inverter systems via the SolarkCloud API.

## Features

- Retrieve yearly, monthly, daily, and flow energy data from the SolarkCloud monitoring platform
- Output in JSON, CSV, or rich terminal table format
- Fully configurable via environment variables or CLI arguments
- Hierarchical, self-documenting command help at every level

## Installation

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo-url>
cd solark-cloud-cli
make install
```

## Configuration

All configuration is driven by environment variables or CLI arguments. CLI arguments take precedence over environment variables, which take precedence over defaults.

| Environment Variable | CLI Flag | Description | Default |
|---------------------|----------|-------------|---------|
| `SOLARK_USERNAME` | `--username`, `-u` | SolarkCloud account email | *(required)* |
| `SOLARK_PASSWORD` | `--password`, `-p` | SolarkCloud account password | *(required)* |
| `SOLARK_PLANT_ID` | `--plant-id` | Plant ID (from your SolarkCloud URL) | *(required)* |
| `SOLARK_API_URL` | | API base URL | `https://api.solarkcloud.com` |
| `SOLARK_OUTPUT_FORMAT` | `--output-format`, `-o` | Output format: `json`, `csv`, `table` | `table` |
| `SOLARK_TIMEOUT` | | HTTP request timeout in seconds | `30` |

Create a `.env` file from the example:

```bash
cp .env.example .env
# Edit .env with your credentials
```

To view current configuration:

```bash
solark config show
```

### Finding your Plant ID

Your plant ID is in your SolarkCloud URL: `https://www.solarkcloud.com/plants/overview/{PLANT_ID}/...`

## Usage

### Yearly energy data (monthly breakdown)

```bash
solark energy year --date 2025
```

### Monthly energy data (daily breakdown)

```bash
solark energy month --date 2025-04
```

### Daily energy data (5-minute intervals)

```bash
solark energy day --date 2025-04-15
```

### Energy flow snapshot

```bash
solark energy flow --date 2025-04-15
```

### Output formats

```bash
# Rich terminal table (default)
solark energy year --date 2025

# JSON
solark energy year --date 2025 --output-format json

# CSV
solark energy year --date 2025 --output-format csv
```

### Inline credentials (override env vars)

```bash
solark energy year --date 2025 --plant-id 125647 --username user@example.com --password mypass
```

### Help at any level

```bash
solark --help
solark energy --help
solark energy year --help
solark config --help
```

## Data Labels

Energy endpoints return these metrics (all in kWh):

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

### Available make targets

```
make help       Show all available targets
make install    Install project dependencies
make dev        Install with dev dependencies
make test       Run tests
make lint       Lint code with ruff
make format     Format code with ruff
make coverage   Run tests with coverage report
make clean      Remove build artifacts and cache
make run        Run the CLI (pass args via ARGS="...")
```

### Running tests

```bash
make test           # Run all tests
make coverage       # Run with coverage report
make run ARGS="energy year --date 2025 --output-format json"
```

### Project structure

```
src/solark_cloud_cli/
├── main.py              # Typer app entry point
├── config.py            # pydantic-settings configuration
├── commands/            # CLI subcommands (energy, config)
├── client/              # HTTP client, auth, URL building
├── services/            # Business logic layer
├── models/              # Pydantic models (API + domain)
└── formatters/          # Output formatting (JSON, CSV, table)
```

### Architecture

The project follows SOLID principles with clear separation of concerns:

- **CLI layer** (`commands/`) — argument parsing and output display
- **Service layer** (`services/`) — business logic and data transformation
- **Client layer** (`client/`) — HTTP communication and authentication
- **Models** (`models/`) — API response models and domain models
- **Formatters** (`formatters/`) — pluggable output formatting via Protocol

## API Notes

The SolarkCloud API is not officially documented. The endpoints used by this tool were confirmed through testing and community research. The API may change without notice.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
