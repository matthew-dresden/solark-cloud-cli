import httpx

from solark_cloud_cli.client.auth import SolarkAuthenticator
from solark_cloud_cli.client.endpoints import EndpointBuilder
from solark_cloud_cli.config import SolarkConfig
from solark_cloud_cli.models.api_responses import ApiResponse
from solark_cloud_cli.models.auth import TokenData


class SolarkClient:
    def __init__(self, config: SolarkConfig) -> None:
        if not config.username:
            msg = "SOLARK_USERNAME is required. Set it via environment variable or --username flag."
            raise ValueError(msg)
        if not config.password:
            msg = "SOLARK_PASSWORD is required. Set it via environment variable or --password flag."
            raise ValueError(msg)
        self._config = config
        self._endpoints = EndpointBuilder(config.api_url)
        self._authenticator = SolarkAuthenticator(
            api_url=config.api_url,
            username=config.username,
            password=config.password,
            timeout=config.timeout,
        )
        self._token: TokenData | None = None
        self._http_client: httpx.Client | None = None

    def __enter__(self) -> "SolarkClient":
        self._http_client = httpx.Client(timeout=self._config.timeout)
        return self

    def __exit__(self, *args: object) -> None:
        if self._http_client:
            self._http_client.close()
            self._http_client = None

    def _ensure_authenticated(self) -> TokenData:
        if self._token is None:
            self._token = self._authenticator.authenticate()
        return self._token

    def _get(self, url: str) -> ApiResponse:
        if self._http_client is None:
            msg = "SolarkClient must be used as a context manager"
            raise RuntimeError(msg)
        token = self._ensure_authenticated()
        response = self._http_client.get(
            url,
            headers={
                "Authorization": f"Bearer {token.access_token}",
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
        api_response = ApiResponse.model_validate(response.json())
        if not api_response.success:
            msg = f"API request failed: {api_response.msg}"
            raise RuntimeError(msg)
        return api_response

    def get_energy_year(self, plant_id: str, date: str) -> ApiResponse:
        url = self._endpoints.energy_year_url(plant_id, date)
        return self._get(url)

    def get_energy_month(self, plant_id: str, date: str) -> ApiResponse:
        url = self._endpoints.energy_month_url(plant_id, date)
        return self._get(url)

    def get_energy_day(self, plant_id: str, date: str) -> ApiResponse:
        url = self._endpoints.energy_day_url(plant_id, date)
        return self._get(url)
