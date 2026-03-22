from solark_cloud_cli.config import SolarkConfig
from solark_cloud_cli.services.config_service import ConfigService


class TestConfigService:
    def test_masks_password(self, sample_config):
        service = ConfigService(sample_config)
        entries = service.get_display_entries()
        password_entry = next(e for e in entries if e.env_var == "SOLARK_PASSWORD")
        assert password_entry.value == "****"

    def test_shows_all_env_vars(self, sample_config):
        service = ConfigService(sample_config)
        entries = service.get_display_entries()
        env_vars = {e.env_var for e in entries}
        expected = {
            "SOLARK_USERNAME",
            "SOLARK_PASSWORD",
            "SOLARK_PLANT_ID",
            "SOLARK_API_URL",
            "SOLARK_OUTPUT_FORMAT",
            "SOLARK_TIMEOUT",
        }
        assert expected.issubset(env_vars)

    def test_shows_not_set_for_none_values(self):
        config = SolarkConfig()
        service = ConfigService(config)
        entries = service.get_display_entries()
        username_entry = next(e for e in entries if e.env_var == "SOLARK_USERNAME")
        assert username_entry.value == "(not set)"
