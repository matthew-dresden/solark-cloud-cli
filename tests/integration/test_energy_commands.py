import pytest
import httpx
import respx
from typer.testing import CliRunner
from solark_cloud_cli.main import app
from tests.conftest import make_token_response_dict, make_api_response_dict

runner = CliRunner()


class TestEnergyCommands:
    @respx.mock
    @pytest.mark.parametrize(
        "subcommand,date_arg",
        [
            pytest.param("year", "2024", id="year"),
            pytest.param("month", "2024-06", id="month"),
            pytest.param("day", "2024-06-15", id="day"),
        ],
    )
    def test_energy_command_json_output(
        self, subcommand, date_arg, sample_api_url, sample_username, sample_password, sample_plant_id
    ):
        respx.post(f"{sample_api_url}/oauth/token").mock(
            return_value=httpx.Response(200, json=make_token_response_dict())
        )
        respx.get(url__startswith=f"{sample_api_url}/api/v1/plant/energy/").mock(
            return_value=httpx.Response(200, json=make_api_response_dict())
        )
        result = runner.invoke(
            app,
            [
                "energy",
                subcommand,
                "--date",
                date_arg,
                "--plant-id",
                sample_plant_id,
                "--username",
                sample_username,
                "--password",
                sample_password,
                "--output-format",
                "json",
            ],
            env={"SOLARK_API_URL": sample_api_url},
        )
        assert result.exit_code == 0
        assert "plant_id" in result.stdout

    def test_energy_year_missing_plant_id(self):
        result = runner.invoke(
            app,
            [
                "energy",
                "year",
                "--date",
                "2024",
                "--username",
                "u",
                "--password",
                "p",
            ],
            env={"SOLARK_API_URL": "https://test.example.com"},
        )
        assert result.exit_code == 1

    def test_top_level_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "energy" in result.stdout
        assert "config" in result.stdout

    def test_energy_help(self):
        result = runner.invoke(app, ["energy", "--help"])
        assert result.exit_code == 0
        assert "year" in result.stdout
        assert "month" in result.stdout
        assert "day" in result.stdout

    @pytest.mark.parametrize("subcommand", ["year", "month", "day"])
    def test_subcommand_help_shows_options(self, subcommand):
        result = runner.invoke(app, ["energy", subcommand, "--help"])
        assert result.exit_code == 0
        assert "--date" in result.stdout
        assert "--plant-id" in result.stdout
        assert "--output-format" in result.stdout
