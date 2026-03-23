from typing import Protocol

from solark_cloud_cli.models.energy import EnergyReport


class Formatter(Protocol):
    def format(self, report: EnergyReport) -> str: ...


def get_formatter(format_name: str, plant_url: str = "", username: str | None = None) -> Formatter:
    from solark_cloud_cli.formatters.csv_formatter import CsvFormatter
    from solark_cloud_cli.formatters.html_formatter import HtmlFormatter
    from solark_cloud_cli.formatters.json_formatter import JsonFormatter
    from solark_cloud_cli.formatters.table_formatter import TableFormatter

    formatters: dict[str, Formatter] = {
        "json": JsonFormatter(),
        "csv": CsvFormatter(),
        "table": TableFormatter(),
        "html": HtmlFormatter(plant_url=plant_url, username=username),
    }
    formatter = formatters.get(format_name)
    if formatter is None:
        msg = f"Unknown output format: '{format_name}'. Must be one of: {', '.join(sorted(formatters.keys()))}"
        raise ValueError(msg)
    return formatter
