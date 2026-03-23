import logging

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class SolarkConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SOLARK_", env_file=".env", env_file_encoding="utf-8", extra="ignore")

    username: str | None = None
    password: str | None = None
    plant_id: str | None = None
    api_url: str = "https://api.solarkcloud.com"
    output_format: str = "table"
    timeout: int = 30
    timezone: str | None = None  # IANA timezone (e.g. "America/Detroit"), defaults to OS local

    # Rate configuration — season boundaries (MM-DD format)
    rate_summer_start: str = "06-01"
    rate_summer_end: str = "09-30"

    # Blended average rates ($/kWh) — used for year and month value calculations
    rate_summer_inflow: float | None = None
    rate_summer_outflow: float | None = None
    rate_nonsummer_inflow: float | None = None
    rate_nonsummer_outflow: float | None = None

    # Time-of-use peak period definition
    rate_peak_start: str = "15:00"
    rate_peak_end: str = "19:00"
    rate_peak_days: str = "mon,tue,wed,thu,fri"

    # Granular TOU rates ($/kWh) — on-peak and off-peak by season
    rate_summer_peak_inflow: float | None = None
    rate_summer_offpeak_inflow: float | None = None
    rate_summer_peak_outflow: float | None = None
    rate_summer_offpeak_outflow: float | None = None
    rate_nonsummer_peak_inflow: float | None = None
    rate_nonsummer_offpeak_inflow: float | None = None
    rate_nonsummer_peak_outflow: float | None = None
    rate_nonsummer_offpeak_outflow: float | None = None

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        allowed = {"json", "csv", "table", "html"}
        if v not in allowed:
            msg = f"output_format must be one of {allowed}, got '{v}'"
            raise ValueError(msg)
        return v

    def has_rate_config(self) -> bool:
        """Return True if blended rate config is available for value calculations."""
        result = all(
            [
                self.rate_summer_inflow is not None,
                self.rate_summer_outflow is not None,
                self.rate_nonsummer_inflow is not None,
                self.rate_nonsummer_outflow is not None,
            ]
        )
        logger.debug("Rate config check: has_config=%s", result)
        return result

    def is_summer_month(self, month: int) -> bool:
        """Determine if a month number (1-12) falls in the summer season."""
        start_month = int(self.rate_summer_start.split("-")[0])
        end_month = int(self.rate_summer_end.split("-")[0])
        return start_month <= month <= end_month
