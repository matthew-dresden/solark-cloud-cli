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


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"solark {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", help="Show version and exit.", callback=_version_callback, is_eager=True),
    ] = None,
) -> None:
    """SolarkCloud CLI — retrieve energy data from Sol-Ark solar inverter systems."""
