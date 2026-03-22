from typing import Annotated, Optional

import typer

from solark_cloud_cli.client.http_client import SolarkClient
from solark_cloud_cli.config import SolarkConfig
from solark_cloud_cli.formatters import get_formatter
from solark_cloud_cli.services.energy_service import EnergyService

energy_app = typer.Typer(
    name="energy",
    help="Retrieve energy production data (yearly, monthly, or daily).",
    no_args_is_help=True,
)

_PERIOD_TO_METHOD = {
    "yearly": "get_yearly_energy",
    "monthly": "get_monthly_energy",
    "daily": "get_daily_energy",
}


def _build_config(
    username: str | None,
    password: str | None,
    plant_id: str | None,
    output_format: str | None,
) -> SolarkConfig:
    """Build config merging CLI args over env vars. CLI args that are None fall through to env/default."""
    overrides: dict[str, object] = {}
    if username is not None:
        overrides["username"] = username
    if password is not None:
        overrides["password"] = password
    if plant_id is not None:
        overrides["plant_id"] = plant_id
    if output_format is not None:
        overrides["output_format"] = output_format
    return SolarkConfig(**overrides)


def _resolve_plant_id(config: SolarkConfig) -> str:
    if not config.plant_id:
        typer.echo("Error: --plant-id is required (or set SOLARK_PLANT_ID environment variable).", err=True)
        raise typer.Exit(code=1)
    return config.plant_id


def _run_energy_command(
    period: str,
    date: str,
    username: str | None,
    password: str | None,
    plant_id: str | None,
    output_format: str | None,
) -> None:
    try:
        config = _build_config(username, password, plant_id, output_format)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e

    resolved_plant_id = _resolve_plant_id(config)

    try:
        formatter = get_formatter(config.output_format)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e

    method_name = _PERIOD_TO_METHOD[period]

    try:
        with SolarkClient(config) as client:
            service = EnergyService(client)
            method = getattr(service, method_name)
            report = method(resolved_plant_id, date)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e

    output = formatter.format(report)
    typer.echo(output)


# Common option definitions to avoid repetition
UsernameOption = Annotated[
    Optional[str],
    typer.Option(
        "--username",
        "-u",
        help="SolarkCloud username/email. [env: SOLARK_USERNAME]",
        envvar="SOLARK_USERNAME",
        show_envvar=False,
    ),
]
PasswordOption = Annotated[
    Optional[str],
    typer.Option(
        "--password",
        "-p",
        help="SolarkCloud password. [env: SOLARK_PASSWORD]",
        envvar="SOLARK_PASSWORD",
        show_envvar=False,
    ),
]
PlantIdOption = Annotated[
    Optional[str],
    typer.Option(
        "--plant-id",
        help="Plant ID. [env: SOLARK_PLANT_ID]",
        envvar="SOLARK_PLANT_ID",
        show_envvar=False,
    ),
]
OutputFormatOption = Annotated[
    Optional[str],
    typer.Option(
        "--output-format",
        "-o",
        help="Output format: json, csv, table. [env: SOLARK_OUTPUT_FORMAT]",
        envvar="SOLARK_OUTPUT_FORMAT",
        show_envvar=False,
    ),
]


@energy_app.command()
def year(
    date: Annotated[str, typer.Option("--date", "-d", help="Year to retrieve data for (format: YYYY).")],
    plant_id: PlantIdOption = None,
    output_format: OutputFormatOption = None,
    username: UsernameOption = None,
    password: PasswordOption = None,
) -> None:
    """Retrieve monthly energy breakdown for an entire year."""
    _run_energy_command("yearly", date, username, password, plant_id, output_format)


@energy_app.command()
def month(
    date: Annotated[str, typer.Option("--date", "-d", help="Month to retrieve data for (format: YYYY-MM).")],
    plant_id: PlantIdOption = None,
    output_format: OutputFormatOption = None,
    username: UsernameOption = None,
    password: PasswordOption = None,
) -> None:
    """Retrieve daily energy breakdown for a specific month."""
    _run_energy_command("monthly", date, username, password, plant_id, output_format)


@energy_app.command()
def day(
    date: Annotated[str, typer.Option("--date", "-d", help="Day to retrieve data for (format: YYYY-MM-DD).")],
    plant_id: PlantIdOption = None,
    output_format: OutputFormatOption = None,
    username: UsernameOption = None,
    password: PasswordOption = None,
) -> None:
    """Retrieve 5-minute interval energy data for a specific day."""
    _run_energy_command("daily", date, username, password, plant_id, output_format)
