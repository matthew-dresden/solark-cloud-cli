import csv
import io

from solark_cloud_cli.models.energy import EnergyReport


class CsvFormatter:
    def format(self, report: EnergyReport) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["timestamp", "label", "value", "unit"])
        for record in report.records:
            writer.writerow([record.timestamp, record.label, record.value, record.unit])
        return output.getvalue()
