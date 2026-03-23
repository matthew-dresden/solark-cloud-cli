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

    def test_table_shows_value_columns_when_valuations_present(self):
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
        formatter = TableFormatter()
        output = formatter.format(report)
        assert "Self-Used" in output
        assert "Avoided $" in output
        assert "Export $" in output
        assert "Value $" in output
        assert "TOTAL" in output

    def test_table_no_value_columns_without_valuations(self):
        report = make_energy_report()
        formatter = TableFormatter()
        output = formatter.format(report)
        assert "Avoided $" not in output
        assert "TOTAL" not in output
