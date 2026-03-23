import logging

from solark_cloud_cli.client.http_client import SolarkClient
from solark_cloud_cli.models.api_responses import ApiResponse
from solark_cloud_cli.models.energy import EnergyRecord, EnergyReport

logger = logging.getLogger(__name__)


class EnergyService:
    def __init__(self, client: SolarkClient) -> None:
        self._client = client

    def get_yearly_energy(self, plant_id: str, date: str) -> EnergyReport:
        response = self._client.get_energy_year(plant_id, date)
        return self._to_report(response, plant_id, "year", date)

    def get_monthly_energy(self, plant_id: str, date: str) -> EnergyReport:
        response = self._client.get_energy_month(plant_id, date)
        return self._to_report(response, plant_id, "month", date)

    def get_month_summary(self, plant_id: str, date: str) -> EnergyReport:
        """Fetch yearly data and filter to a single month's aggregate row.

        Args:
            plant_id: The plant ID.
            date: Month in YYYY-MM format.
        """
        parts = date.split("-")
        year = parts[0]
        month_key = date  # e.g. "2025-07"
        logger.info("Fetching month summary for %s from year %s", month_key, year)

        year_report = self.get_yearly_energy(plant_id, year)
        filtered_records = [r for r in year_report.records if r.timestamp == month_key]

        if not filtered_records:
            msg = f"No data found for month {month_key} in year {year}"
            raise ValueError(msg)

        return EnergyReport(
            plant_id=plant_id,
            period="year",
            date=month_key,
            records=filtered_records,
            labels=year_report.labels,
        )

    def get_daily_energy(self, plant_id: str, date: str) -> EnergyReport:
        response = self._client.get_energy_day(plant_id, date)
        return self._to_report(response, plant_id, "day", date)

    @staticmethod
    def _to_report(response: ApiResponse, plant_id: str, period: str, date: str) -> EnergyReport:
        logger.info("Transforming API response: %d infos, period=%s", len(response.data.infos), period)
        records: list[EnergyRecord] = []
        labels: list[str] = []
        for info in response.data.infos:
            if info.label not in labels:
                labels.append(info.label)
            for record in info.records:
                records.append(
                    EnergyRecord(
                        timestamp=record.time,
                        value=float(record.value),
                        unit=info.unit,
                        label=info.label,
                    )
                )
        logger.debug("Transformed %d records across %d labels", len(records), len(labels))
        return EnergyReport(
            plant_id=plant_id,
            period=period,
            date=date,
            records=records,
            labels=labels,
        )
