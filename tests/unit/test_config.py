import pytest
from solark_cloud_cli.config import SolarkConfig


class TestSolarkConfig:
    def test_loads_from_explicit_values(self, sample_username, sample_password, sample_api_url):
        config = SolarkConfig(username=sample_username, password=sample_password, api_url=sample_api_url)
        assert config.username == sample_username
        assert config.password == sample_password
        assert config.api_url == sample_api_url

    def test_loads_from_env_vars(self, monkeypatch, sample_username, sample_password):
        monkeypatch.setenv("SOLARK_USERNAME", sample_username)
        monkeypatch.setenv("SOLARK_PASSWORD", sample_password)
        monkeypatch.setenv("SOLARK_PLANT_ID", "12345")
        config = SolarkConfig()
        assert config.username == sample_username
        assert config.password == sample_password
        assert config.plant_id == "12345"

    def test_default_values(self):
        config = SolarkConfig()
        assert config.api_url == "https://api.solarkcloud.com"
        assert config.output_format == "table"
        assert config.timeout == 30

    @pytest.mark.parametrize(
        "invalid_format",
        [
            pytest.param("xml", id="xml"),
            pytest.param("yaml", id="yaml"),
            pytest.param("", id="empty"),
        ],
    )
    def test_rejects_invalid_output_format(self, invalid_format):
        with pytest.raises(Exception):
            SolarkConfig(output_format=invalid_format)

    @pytest.mark.parametrize(
        "valid_format",
        [
            pytest.param("json", id="json"),
            pytest.param("csv", id="csv"),
            pytest.param("table", id="table"),
            pytest.param("html", id="html"),
        ],
    )
    def test_accepts_valid_output_format(self, valid_format):
        config = SolarkConfig(output_format=valid_format)
        assert config.output_format == valid_format

    def test_has_rate_config_when_all_set(self):
        config = SolarkConfig(
            rate_summer_inflow=0.22,
            rate_summer_outflow=0.10,
            rate_nonsummer_inflow=0.23,
            rate_nonsummer_outflow=0.10,
        )
        assert config.has_rate_config() is True

    def test_has_rate_config_when_missing(self):
        config = SolarkConfig()
        assert config.has_rate_config() is False

    def test_has_rate_config_partial(self):
        config = SolarkConfig(rate_summer_inflow=0.22)
        assert config.has_rate_config() is False

    @pytest.mark.parametrize(
        "month,expected",
        [
            pytest.param(6, True, id="june-summer"),
            pytest.param(9, True, id="september-summer"),
            pytest.param(1, False, id="january-nonsummer"),
            pytest.param(12, False, id="december-nonsummer"),
        ],
    )
    def test_is_summer_month(self, month, expected):
        config = SolarkConfig()
        assert config.is_summer_month(month) == expected

    def test_loads_from_env_file(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("SOLARK_PLANT_ID=env-file-plant\nSOLARK_RATE_SUMMER_INFLOW=0.55\n")
        monkeypatch.chdir(tmp_path)
        config = SolarkConfig(_env_file=str(env_file))
        assert config.plant_id == "env-file-plant"
        assert config.rate_summer_inflow == 0.55
