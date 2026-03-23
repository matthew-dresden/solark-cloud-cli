import pytest
from solark_cloud_cli.formatters.html_formatter import HtmlFormatter
from solark_cloud_cli.models.energy import ValuationRow
from tests.conftest import make_energy_report


class TestHtmlFormatter:
    @pytest.fixture
    def formatter(self):
        return HtmlFormatter(
            plant_url="https://www.solarkcloud.com/plants/overview/999999", username="test@example.com"
        )

    @pytest.mark.parametrize(
        "num_labels,num_records",
        [
            pytest.param(2, 3, id="standard"),
            pytest.param(1, 1, id="minimal"),
            pytest.param(6, 12, id="full-year"),
        ],
    )
    def test_html_is_valid_document(self, formatter, num_labels, num_records):
        labels = [f"M{i}" for i in range(num_labels)]
        report = make_energy_report(labels=labels, records_per_label=num_records)
        output = formatter.format(report)
        assert output.startswith("<!DOCTYPE html>")
        assert "</html>" in output
        assert "<table>" in output

    def test_html_contains_plant_id(self, formatter):
        report = make_energy_report(plant_id="plant-42")
        output = formatter.format(report)
        assert "plant-42" in output

    def test_html_contains_solarkcloud_link(self, formatter):
        report = make_energy_report()
        output = formatter.format(report)
        assert "https://www.solarkcloud.com/plants/overview/999999" in output

    def test_html_contains_username(self, formatter):
        report = make_energy_report()
        output = formatter.format(report)
        assert "test@example.com" in output

    def test_html_dark_mode(self, formatter):
        report = make_energy_report()
        output = formatter.format(report)
        assert "#0d1117" in output  # dark background color

    def test_html_contains_labels_as_headers(self, formatter):
        labels = ["Load", "PV", "Export"]
        report = make_energy_report(labels=labels, records_per_label=1)
        output = formatter.format(report)
        for label in labels:
            assert f"<th>{label}</th>" in output

    def test_html_with_valuations(self, formatter):
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
        output = formatter.format(report)
        assert "Self-Used" in output
        assert "Avoided $" in output
        assert "Export $" in output
        assert "Value $" in output
        assert "TOTAL" in output
        assert "$32.64" in output

    def test_html_without_valuations_no_value_columns(self, formatter):
        report = make_energy_report()
        output = formatter.format(report)
        assert "Avoided $" not in output
        assert "TOTAL" not in output

    def test_html_contains_version(self, formatter):
        from solark_cloud_cli import __version__

        report = make_energy_report()
        output = formatter.format(report)
        assert __version__ in output

    def test_html_no_username_shows_dash(self):
        formatter = HtmlFormatter(plant_url="https://example.com", username=None)
        report = make_energy_report()
        output = formatter.format(report)
        assert "<strong>Account:</strong> —" in output
