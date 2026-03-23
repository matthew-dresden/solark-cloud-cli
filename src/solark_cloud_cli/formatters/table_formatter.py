import io

from rich.console import Console
from rich.table import Table

from solark_cloud_cli.models.energy import EnergyReport


class TableFormatter:
    def format(self, report: EnergyReport) -> str:
        has_values = report.valuations is not None and len(report.valuations) > 0

        table = Table(title=f"Energy Data — {report.period} — {report.date} — Plant {report.plant_id}")

        # Build pivot table: rows are timestamps, columns are labels
        labels = report.labels
        table.add_column("Time", style="cyan")
        for label in labels:
            table.add_column(label, justify="right", style="green")

        if has_values:
            table.add_column("Self-Used", justify="right", style="yellow")
            table.add_column("Avoided $", justify="right", style="bold green")
            table.add_column("Export $", justify="right", style="bold green")
            table.add_column("Value $", justify="right", style="bold magenta")

        # Group energy records by timestamp
        by_time: dict[str, dict[str, float]] = {}
        for record in report.records:
            if record.timestamp not in by_time:
                by_time[record.timestamp] = {}
            by_time[record.timestamp][record.label] = record.value

        # Index valuations by timestamp
        val_by_time: dict[str, object] = {}
        if has_values:
            for v in report.valuations:
                val_by_time[v.timestamp] = v

        # Track totals
        energy_totals: dict[str, float] = {label: 0.0 for label in labels}
        val_totals = {"self_consumed": 0.0, "avoided": 0.0, "export_credit": 0.0, "total": 0.0}

        for timestamp in sorted(by_time.keys()):
            row_data = by_time[timestamp]
            row = [timestamp]
            for label in labels:
                val = row_data.get(label)
                if val is not None:
                    energy_totals[label] += val
                row.append(f"{val:,.1f}" if val is not None else "—")

            if has_values:
                v = val_by_time.get(timestamp)
                if v is not None:
                    val_totals["self_consumed"] += v.self_consumed_kwh
                    val_totals["avoided"] += v.avoided_cost
                    val_totals["export_credit"] += v.export_credit
                    val_totals["total"] += v.total_value
                    row.append(f"{v.self_consumed_kwh:,.1f}")
                    row.append(f"${v.avoided_cost:,.2f}")
                    row.append(f"${v.export_credit:,.2f}")
                    row.append(f"${v.total_value:,.2f}")
                else:
                    row.extend(["—", "—", "—", "—"])

            table.add_row(*row)

        # Add totals row
        if has_values:
            totals_row = ["TOTAL"]
            for label in labels:
                totals_row.append(f"{energy_totals[label]:,.1f}")
            totals_row.append(f"{val_totals['self_consumed']:,.1f}")
            totals_row.append(f"${val_totals['avoided']:,.2f}")
            totals_row.append(f"${val_totals['export_credit']:,.2f}")
            totals_row.append(f"${val_totals['total']:,.2f}")
            table.add_row(*totals_row, style="bold")

        output = io.StringIO()
        console = Console(file=output, force_terminal=False, width=200)
        console.print(table)
        return output.getvalue()
