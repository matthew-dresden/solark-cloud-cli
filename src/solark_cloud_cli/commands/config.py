import typer
from rich.console import Console
from rich.table import Table

from solark_cloud_cli.config import SolarkConfig
from solark_cloud_cli.services.config_service import ConfigService

config_app = typer.Typer(
    name="config",
    help="View and inspect configuration.",
    no_args_is_help=True,
)


@config_app.command()
def show() -> None:
    """Display all configuration values and their sources."""
    config = SolarkConfig()
    service = ConfigService(config)
    entries = service.get_display_entries()

    table = Table(title="SolarkCloud CLI Configuration")
    table.add_column("Environment Variable", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Status", style="yellow")

    for entry in entries:
        status = "set" if entry.is_set else "default"
        table.add_row(entry.env_var, entry.value, status)

    console = Console()
    console.print(table)
