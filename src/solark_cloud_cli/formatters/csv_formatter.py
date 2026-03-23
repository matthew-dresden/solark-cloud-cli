import csv
import io

from solark_cloud_cli.models.energy import EnergyReport


class CsvFormatter:
    def format(self, report: EnergyReport) -> str:
        has_values = report.valuations is not None and len(report.valuations) > 0
        output = io.StringIO()
        writer = csv.writer(output)

        if has_values:
            # Pivot format with value columns
            labels = report.labels
            header = ["timestamp"] + labels + ["self_consumed_kwh", "avoided_cost", "export_credit", "total_value"]
            writer.writerow(header)

            # Group energy records by timestamp
            by_time: dict[str, dict[str, float]] = {}
            for record in report.records:
                if record.timestamp not in by_time:
                    by_time[record.timestamp] = {}
                by_time[record.timestamp][record.label] = record.value

            # Index valuations
            val_by_time = {v.timestamp: v for v in report.valuations}

            for timestamp in sorted(by_time.keys()):
                row_data = by_time[timestamp]
                row = [timestamp]
                for label in labels:
                    row.append(row_data.get(label, 0.0))
                v = val_by_time.get(timestamp)
                if v is not None:
                    row.extend([v.self_consumed_kwh, v.avoided_cost, v.export_credit, v.total_value])
                else:
                    row.extend([0.0, 0.0, 0.0, 0.0])
                writer.writerow(row)
        else:
            writer.writerow(["timestamp", "label", "value", "unit"])
            for record in report.records:
                writer.writerow([record.timestamp, record.label, record.value, record.unit])

        return output.getvalue()
