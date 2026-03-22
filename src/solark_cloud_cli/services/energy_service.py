from solark_cloud_cli.client.http_client import SolarkClient
from solark_cloud_cli.models.api_responses import ApiResponse
from solark_cloud_cli.models.energy import EnergyRecord, EnergyReport


class EnergyService:
    def __init__(self, client: SolarkClient) -> None:
        self._client = client

    def get_yearly_energy(self, plant_id: str, date: str) -> EnergyReport:
        response = self._client.get_energy_year(plant_id, date)
        return self._to_report(response, plant_id, "year", date)

    def get_monthly_energy(self, plant_id: str, date: str) -> EnergyReport:
        response = self._client.get_energy_month(plant_id, date)
        return self._to_report(response, plant_id, "month", date)

    def get_daily_energy(self, plant_id: str, date: str) -> EnergyReport:
        response = self._client.get_energy_day(plant_id, date)
        return self._to_report(response, plant_id, "day", date)

    @staticmethod
    def _to_report(response: ApiResponse, plant_id: str, period: str, date: str) -> EnergyReport:
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
        return EnergyReport(
            plant_id=plant_id,
            period=period,
            date=date,
            records=records,
            labels=labels,
        )
