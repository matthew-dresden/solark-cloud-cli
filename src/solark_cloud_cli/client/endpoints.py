from urllib.parse import urlencode


class EndpointBuilder:
    def __init__(self, api_url: str) -> None:
        self._api_url = api_url.rstrip("/")

    def auth_url(self) -> str:
        return f"{self._api_url}/oauth/token"

    def energy_year_url(self, plant_id: str, date: str) -> str:
        return self._energy_url(plant_id, "year", date)

    def energy_month_url(self, plant_id: str, date: str) -> str:
        return self._energy_url(plant_id, "month", date)

    def energy_day_url(self, plant_id: str, date: str) -> str:
        return self._energy_url(plant_id, "day", date)

    def _energy_url(self, plant_id: str, period: str, date: str) -> str:
        base = f"{self._api_url}/api/v1/plant/energy/{plant_id}/{period}"
        params = urlencode({"date": date, "id": plant_id, "lan": "en"})
        return f"{base}?{params}"
