from typer.testing import CliRunner
from solark_cloud_cli.main import app

runner = CliRunner()


class TestConfigCommands:
    def test_config_show(self):
        result = runner.invoke(
            app,
            ["config", "show"],
            env={
                "SOLARK_USERNAME": "test@example.com",
                "SOLARK_PASSWORD": "secret",
                "SOLARK_PLANT_ID": "12345",
            },
        )
        assert result.exit_code == 0
        assert "SOLARK_USERNAME" in result.stdout
        assert "****" in result.stdout  # password masked
        assert "secret" not in result.stdout  # password NOT shown

    def test_config_help(self):
        result = runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        assert "show" in result.stdout
