import pytest
from solark_cloud_cli.client.endpoints import EndpointBuilder


class TestEndpointBuilder:
    @pytest.mark.parametrize(
        "base_url",
        [
            pytest.param("https://api.example.com", id="no-trailing-slash"),
            pytest.param("https://api.example.com/", id="trailing-slash"),
        ],
    )
    def test_auth_url(self, base_url):
        builder = EndpointBuilder(base_url)
        assert builder.auth_url() == "https://api.example.com/oauth/token"

    @pytest.mark.parametrize(
        "plant_id,date,expected_path",
        [
            pytest.param("111", "2024", "year", id="year"),
            pytest.param("222", "2024-06-01", "month", id="month"),
            pytest.param("333", "2024-06-15", "day", id="day"),
        ],
    )
    def test_energy_urls_contain_plant_id_and_period(self, plant_id, date, expected_path):
        builder = EndpointBuilder("https://api.test.com")
        method = getattr(builder, f"energy_{expected_path}_url")
        url = method(plant_id, date)
        assert f"/plant/energy/{plant_id}/{expected_path}" in url
        assert f"date={date}" in url
        assert f"id={plant_id}" in url
        assert "lan=en" in url
