from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SolarkConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SOLARK_")

    username: str | None = None
    password: str | None = None
    plant_id: str | None = None
    api_url: str = "https://api.solarkcloud.com"
    output_format: str = "table"
    timeout: int = 30

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        allowed = {"json", "csv", "table"}
        if v not in allowed:
            msg = f"output_format must be one of {allowed}, got '{v}'"
            raise ValueError(msg)
        return v
