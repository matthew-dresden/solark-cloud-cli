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
