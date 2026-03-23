import pytest
from unittest.mock import MagicMock
from solark_cloud_cli.models.api_responses import ApiResponse
from solark_cloud_cli.services.energy_service import EnergyService
from tests.conftest import make_api_response_dict


class TestEnergyService:
    @pytest.mark.parametrize(
        "num_labels,num_records",
        [
            pytest.param(4, 12, id="year-four-labels"),
            pytest.param(6, 30, id="month-six-labels"),
            pytest.param(2, 1, id="minimal"),
        ],
    )
    def test_transforms_api_response_to_report(self, num_labels, num_records):
        labels = [f"Metric{i}" for i in range(num_labels)]
        api_dict = make_api_response_dict(labels=labels, records_per_label=num_records)
        api_response = ApiResponse.model_validate(api_dict)

        mock_client = MagicMock()
        mock_client.get_energy_year.return_value = api_response

        service = EnergyService(mock_client)
        report = service.get_yearly_energy("test-plant", "2024")

        assert report.plant_id == "test-plant"
        assert report.period == "year"
        assert report.date == "2024"
        assert len(report.labels) == num_labels
        assert len(report.records) == num_labels * num_records

    @pytest.mark.parametrize(
        "method_name,client_method",
        [
            pytest.param("get_monthly_energy", "get_energy_month", id="monthly"),
            pytest.param("get_daily_energy", "get_energy_day", id="daily"),
        ],
    )
    def test_all_energy_methods(self, method_name, client_method):
        api_dict = make_api_response_dict(labels=["PV"], records_per_label=1)
        api_response = ApiResponse.model_validate(api_dict)

        mock_client = MagicMock()
        setattr(mock_client, client_method, MagicMock(return_value=api_response))

        service = EnergyService(mock_client)
        method = getattr(service, method_name)
        report = method("plant-1", "2024-01")
        assert report.plant_id == "plant-1"
        assert len(report.records) >= 1

    def test_month_summary_filters_to_single_month(self):
        # Year data with 12 months, timestamps 2024-01 through 2024-12
        api_dict = make_api_response_dict(labels=["PV", "Load"], records_per_label=12)
        api_response = ApiResponse.model_validate(api_dict)

        mock_client = MagicMock()
        mock_client.get_energy_year.return_value = api_response

        service = EnergyService(mock_client)
        report = service.get_month_summary("plant-1", "2024-07")

        assert report.plant_id == "plant-1"
        assert report.date == "2024-07"
        assert report.period == "year"
        # Should only have records matching timestamp 2024-07
        for record in report.records:
            assert record.timestamp == "2024-07"

    def test_month_summary_raises_on_missing_month(self):
        # Year data with only 1 record at 2024-01
        api_dict = make_api_response_dict(labels=["PV"], records_per_label=1, time_prefix="2024-")
        api_response = ApiResponse.model_validate(api_dict)

        mock_client = MagicMock()
        mock_client.get_energy_year.return_value = api_response

        service = EnergyService(mock_client)
        with pytest.raises(ValueError, match="No data found for month 2024-12"):
            service.get_month_summary("plant-1", "2024-12")

    def test_converts_string_values_to_float(self):
        api_dict = make_api_response_dict(labels=["PV"], records_per_label=1)
        api_response = ApiResponse.model_validate(api_dict)

        mock_client = MagicMock()
        mock_client.get_energy_year.return_value = api_response

        service = EnergyService(mock_client)
        report = service.get_yearly_energy("plant-1", "2024")
        for record in report.records:
            assert isinstance(record.value, float)
