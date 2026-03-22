from solark_cloud_cli.config import SolarkConfig


class ConfigEntry:
    def __init__(self, env_var: str, value: str, is_set: bool) -> None:
        self.env_var = env_var
        self.value = value
        self.is_set = is_set


class ConfigService:
    _SENSITIVE_FIELDS = frozenset({"password"})

    def __init__(self, config: SolarkConfig) -> None:
        self._config = config

    def get_display_entries(self) -> list[ConfigEntry]:
        entries: list[ConfigEntry] = []
        for field_name, field_info in type(self._config).model_fields.items():
            env_var = f"SOLARK_{field_name.upper()}"
            raw_value = getattr(self._config, field_name)
            is_set = raw_value is not None and raw_value != field_info.default
            if field_name in self._SENSITIVE_FIELDS and raw_value:
                display_value = "****"
            elif raw_value is None:
                display_value = "(not set)"
            else:
                display_value = str(raw_value)
            entries.append(ConfigEntry(env_var=env_var, value=display_value, is_set=is_set))
        return entries
