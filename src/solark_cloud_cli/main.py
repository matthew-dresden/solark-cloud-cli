import logging
import sys
from typing import Annotated, Optional

import typer

from solark_cloud_cli import __version__
from solark_cloud_cli.commands.config import config_app
from solark_cloud_cli.commands.energy import energy_app

app = typer.Typer(
    name="solark",
    help="CLI for the SolarkCloud API — retrieve solar energy production data from Sol-Ark inverters.",
    no_args_is_help=True,
)

app.add_typer(energy_app, name="energy")
app.add_typer(config_app, name="config")

_LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"solark {__version__}")
        raise typer.Exit()


def _configure_logging(level_name: str) -> None:
    level = _LOG_LEVELS.get(level_name.lower())
    if level is None:
        msg = f"Invalid log level: '{level_name}'. Must be one of: {', '.join(_LOG_LEVELS.keys())}"
        raise typer.BadParameter(msg)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        stream=sys.stderr,
    )


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", help="Show version and exit.", callback=_version_callback, is_eager=True),
    ] = None,
    log_level: Annotated[
        str,
        typer.Option(
            "--log-level",
            "-l",
            help="Log level: debug, info, warning, error. [env: SOLARK_LOG_LEVEL]",
            envvar="SOLARK_LOG_LEVEL",
        ),
    ] = "warning",
) -> None:
    """SolarkCloud CLI — retrieve energy data from Sol-Ark solar inverter systems."""
    _configure_logging(log_level)
