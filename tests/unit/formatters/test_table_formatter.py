import pytest
from solark_cloud_cli.formatters.table_formatter import TableFormatter
from tests.conftest import make_energy_report


class TestTableFormatter:
    @pytest.mark.parametrize(
        "num_labels,num_records",
        [
            pytest.param(2, 3, id="standard"),
            pytest.param(1, 1, id="minimal"),
        ],
    )
    def test_table_contains_labels_as_columns(self, num_labels, num_records):
        labels = [f"Metric{i}" for i in range(num_labels)]
        report = make_energy_report(labels=labels, records_per_label=num_records)
        formatter = TableFormatter()
        output = formatter.format(report)
        for label in labels:
            assert label in output

    def test_table_contains_plant_id(self):
        report = make_energy_report(plant_id="test-plant-99")
        formatter = TableFormatter()
        output = formatter.format(report)
        assert "test-plant-99" in output
