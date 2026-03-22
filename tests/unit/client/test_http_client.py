import pytest
import httpx
import respx
from solark_cloud_cli.client.http_client import SolarkClient
from tests.conftest import make_token_response_dict, make_api_response_dict


class TestSolarkClient:
    def test_requires_username(self, sample_api_url, sample_password, sample_plant_id):
        from solark_cloud_cli.config import SolarkConfig

        config = SolarkConfig(password=sample_password, plant_id=sample_plant_id, api_url=sample_api_url)
        with pytest.raises(ValueError, match="SOLARK_USERNAME"):
            SolarkClient(config)

    def test_requires_password(self, sample_api_url, sample_username, sample_plant_id):
        from solark_cloud_cli.config import SolarkConfig

        config = SolarkConfig(username=sample_username, plant_id=sample_plant_id, api_url=sample_api_url)
        with pytest.raises(ValueError, match="SOLARK_PASSWORD"):
            SolarkClient(config)

    def test_requires_context_manager(self, sample_config):
        client = SolarkClient(sample_config)
        with pytest.raises(RuntimeError, match="context manager"):
            client.get_energy_year("123", "2024")

    @respx.mock
    def test_get_energy_year(self, sample_config, sample_plant_id):
        token_data = make_token_response_dict()
        api_data = make_api_response_dict()
        respx.post(f"{sample_config.api_url}/oauth/token").mock(return_value=httpx.Response(200, json=token_data))
        respx.get(url__startswith=f"{sample_config.api_url}/api/v1/plant/energy/{sample_plant_id}/year").mock(
            return_value=httpx.Response(200, json=api_data)
        )
        with SolarkClient(sample_config) as client:
            response = client.get_energy_year(sample_plant_id, "2024")
        assert response.success is True
        assert len(response.data.infos) == len(api_data["data"]["infos"])

    @respx.mock
    @pytest.mark.parametrize(
        "method_name,period",
        [
            pytest.param("get_energy_month", "month", id="month"),
            pytest.param("get_energy_day", "day", id="day"),
        ],
    )
    def test_get_energy_methods(self, sample_config, sample_plant_id, method_name, period):
        token_data = make_token_response_dict()
        api_data = make_api_response_dict(records_per_label=1)
        respx.post(f"{sample_config.api_url}/oauth/token").mock(return_value=httpx.Response(200, json=token_data))
        respx.get(url__startswith=f"{sample_config.api_url}/api/v1/plant/energy/{sample_plant_id}/{period}").mock(
            return_value=httpx.Response(200, json=api_data)
        )
        with SolarkClient(sample_config) as client:
            method = getattr(client, method_name)
            response = method(sample_plant_id, "2024-01-01")
        assert response.success is True
