import json
import pytest
from solark_cloud_cli.formatters.json_formatter import JsonFormatter
from tests.conftest import make_energy_report


class TestJsonFormatter:
    @pytest.mark.parametrize(
        "num_labels,num_records",
        [
            pytest.param(2, 3, id="standard"),
            pytest.param(1, 1, id="minimal"),
            pytest.param(6, 12, id="full-year"),
        ],
    )
    def test_output_is_valid_json(self, num_labels, num_records):
        labels = [f"M{i}" for i in range(num_labels)]
        report = make_energy_report(labels=labels, records_per_label=num_records)
        formatter = JsonFormatter()
        output = formatter.format(report)
        parsed = json.loads(output)
        assert parsed["plant_id"] == report.plant_id
        assert len(parsed["records"]) == num_labels * num_records

    def test_roundtrip(self):
        report = make_energy_report()
        formatter = JsonFormatter()
        output = formatter.format(report)
        parsed = json.loads(output)
        assert parsed["period"] == report.period
        assert parsed["date"] == report.date
