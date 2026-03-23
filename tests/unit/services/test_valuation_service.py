import pytest
from solark_cloud_cli.services.valuation_service import ValuationService
from tests.conftest import make_energy_report_with_values


class TestValuationService:
    def test_requires_rate_config(self, sample_config):
        """ValuationService should fail fast if rate config is missing."""
        with pytest.raises(ValueError, match="Rate configuration is required"):
            ValuationService(sample_config)

    def test_adds_valuations_to_year_report(self, sample_rate_config):
        report = make_energy_report_with_values(period="year", time_prefix="2024-", records_per_label=12)
        service = ValuationService(sample_rate_config)
        valued = service.add_valuations(report)
        assert valued.valuations is not None
        assert len(valued.valuations) == 12

    def test_adds_valuations_to_month_report(self, sample_rate_config):
        report = make_energy_report_with_values(period="month", time_prefix="2024-06-", records_per_label=5)
        service = ValuationService(sample_rate_config)
        valued = service.add_valuations(report)
        assert valued.valuations is not None
        assert len(valued.valuations) == 5

    def test_skips_day_period(self, sample_rate_config):
        report = make_energy_report_with_values(period="day", records_per_label=3)
        service = ValuationService(sample_rate_config)
        valued = service.add_valuations(report)
        assert valued.valuations is None

    def test_applies_summer_rates(self, sample_rate_config):
        """Summer months should use summer rates."""
        report = make_energy_report_with_values(period="year", time_prefix="2024-", records_per_label=1)
        # Record at 2024-07 (July = summer)
        report = report.model_copy(
            update={
                "records": [r.model_copy(update={"timestamp": "2024-07"}) for r in report.records],
            }
        )
        service = ValuationService(sample_rate_config)
        valued = service.add_valuations(report)
        assert valued.valuations is not None
        assert len(valued.valuations) == 1
        v = valued.valuations[0]
        # Self-consumed = Load - Import
        load = next(r.value for r in report.records if r.label == "Load")
        grid_import = next(r.value for r in report.records if r.label == "Import")
        export = next(r.value for r in report.records if r.label == "Export")
        expected_self = load - grid_import
        expected_avoided = round(expected_self * sample_rate_config.rate_summer_inflow, 2)
        expected_export_credit = round(export * sample_rate_config.rate_summer_outflow, 2)
        assert v.self_consumed_kwh == round(expected_self, 1)
        assert v.avoided_cost == expected_avoided
        assert v.export_credit == expected_export_credit
        assert v.total_value == round(expected_avoided + expected_export_credit, 2)

    def test_applies_nonsummer_rates(self, sample_rate_config):
        """Non-summer months should use non-summer rates."""
        report = make_energy_report_with_values(period="year", time_prefix="2024-", records_per_label=1)
        report = report.model_copy(
            update={
                "records": [r.model_copy(update={"timestamp": "2024-01"}) for r in report.records],
            }
        )
        service = ValuationService(sample_rate_config)
        valued = service.add_valuations(report)
        v = valued.valuations[0]
        load = next(r.value for r in report.records if r.label == "Load")
        grid_import = next(r.value for r in report.records if r.label == "Import")
        export = next(r.value for r in report.records if r.label == "Export")
        expected_avoided = round((load - grid_import) * sample_rate_config.rate_nonsummer_inflow, 2)
        expected_export = round(export * sample_rate_config.rate_nonsummer_outflow, 2)
        assert v.avoided_cost == expected_avoided
        assert v.export_credit == expected_export

    def test_valuations_total_is_sum_of_parts(self, sample_rate_config):
        report = make_energy_report_with_values(period="year", time_prefix="2024-", records_per_label=6)
        service = ValuationService(sample_rate_config)
        valued = service.add_valuations(report)
        for v in valued.valuations:
            assert v.total_value == round(v.avoided_cost + v.export_credit, 2)

    @pytest.mark.parametrize(
        "summer_start,summer_end,test_month,expect_summer",
        [
            pytest.param("06-01", "09-30", 7, True, id="july-is-summer"),
            pytest.param("06-01", "09-30", 1, False, id="january-is-nonsummer"),
            pytest.param("06-01", "09-30", 6, True, id="june-boundary-summer"),
            pytest.param("06-01", "09-30", 10, False, id="october-boundary-nonsummer"),
            pytest.param("05-01", "10-31", 5, True, id="custom-may-summer"),
        ],
    )
    def test_season_detection(self, sample_rate_config, summer_start, summer_end, test_month, expect_summer):
        config = sample_rate_config.model_copy(
            update={
                "rate_summer_start": summer_start,
                "rate_summer_end": summer_end,
            }
        )
        assert config.is_summer_month(test_month) == expect_summer
