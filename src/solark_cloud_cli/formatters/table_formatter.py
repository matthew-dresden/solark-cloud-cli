import io

from rich.console import Console
from rich.table import Table

from solark_cloud_cli.models.energy import EnergyReport


class TableFormatter:
    def format(self, report: EnergyReport) -> str:
        table = Table(title=f"Energy Data — {report.period} — {report.date} — Plant {report.plant_id}")

        # Build pivot table: rows are timestamps, columns are labels
        labels = report.labels
        table.add_column("Time", style="cyan")
        for label in labels:
            table.add_column(label, justify="right", style="green")

        # Group records by timestamp
        by_time: dict[str, dict[str, float]] = {}
        for record in report.records:
            if record.timestamp not in by_time:
                by_time[record.timestamp] = {}
            by_time[record.timestamp][record.label] = record.value

        for timestamp in sorted(by_time.keys()):
            row_data = by_time[timestamp]
            row = [timestamp]
            for label in labels:
                val = row_data.get(label)
                row.append(f"{val:,.1f}" if val is not None else "—")
            table.add_row(*row)

        output = io.StringIO()
        console = Console(file=output, force_terminal=False, width=200)
        console.print(table)
        return output.getvalue()
