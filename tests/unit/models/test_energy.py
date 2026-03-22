import pytest
from solark_cloud_cli.models.energy import EnergyRecord
from tests.conftest import make_energy_report


class TestEnergyRecord:
    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(0.0, id="zero"),
            pytest.param(100.5, id="positive"),
            pytest.param(9999.9, id="large"),
        ],
    )
    def test_record_stores_value(self, value):
        record = EnergyRecord(timestamp="2024-01", value=value, unit="kWh", label="PV")
        assert record.value == value


class TestEnergyReport:
    @pytest.mark.parametrize(
        "num_labels,num_records",
        [
            pytest.param(2, 3, id="two-labels-three-records"),
            pytest.param(1, 1, id="single"),
            pytest.param(6, 12, id="full-year-six-labels"),
        ],
    )
    def test_report_has_correct_counts(self, num_labels, num_records):
        labels = [f"Metric{i}" for i in range(num_labels)]
        report = make_energy_report(labels=labels, records_per_label=num_records)
        assert len(report.labels) == num_labels
        assert len(report.records) == num_labels * num_records

    def test_report_serializes_to_dict(self):
        report = make_energy_report()
        data = report.model_dump()
        assert "plant_id" in data
        assert "records" in data
        assert isinstance(data["records"], list)
