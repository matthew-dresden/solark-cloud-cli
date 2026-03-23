import pytest
from solark_cloud_cli.formatters.csv_formatter import CsvFormatter
from tests.conftest import make_energy_report


class TestCsvFormatter:
    @pytest.mark.parametrize(
        "num_labels,num_records",
        [
            pytest.param(2, 3, id="standard"),
            pytest.param(1, 1, id="minimal"),
        ],
    )
    def test_csv_has_header_and_correct_rows(self, num_labels, num_records):
        labels = [f"M{i}" for i in range(num_labels)]
        report = make_energy_report(labels=labels, records_per_label=num_records)
        formatter = CsvFormatter()
        output = formatter.format(report)
        lines = [line.strip() for line in output.strip().splitlines()]
        assert lines[0] == "timestamp,label,value,unit"
        assert len(lines) == 1 + num_labels * num_records  # header + data rows

    def test_csv_contains_record_values(self):
        report = make_energy_report(labels=["PV"], records_per_label=1)
        formatter = CsvFormatter()
        output = formatter.format(report)
        assert "PV" in output
        assert "kWh" in output

    def test_csv_pivoted_with_valuations(self):
        from solark_cloud_cli.models.energy import ValuationRow

        report = make_energy_report(labels=["Load", "PV", "Export", "Import"], records_per_label=2)
        valuations = [
            ValuationRow(
                timestamp=f"2024-{i + 1:02d}",
                self_consumed_kwh=100.0,
                avoided_cost=22.74,
                export_credit=9.90,
                total_value=32.64,
            )
            for i in range(2)
        ]
        report = report.model_copy(update={"valuations": valuations})
        formatter = CsvFormatter()
        output = formatter.format(report)
        lines = output.strip().split("\n")
        assert "self_consumed_kwh" in lines[0]
        assert "avoided_cost" in lines[0]
        assert "total_value" in lines[0]
        assert len(lines) == 3  # header + 2 data rows
