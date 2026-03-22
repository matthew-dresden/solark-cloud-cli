import pytest
import httpx
import respx
from solark_cloud_cli.client.auth import SolarkAuthenticator
from tests.conftest import make_token_response_dict


class TestSolarkAuthenticator:
    @respx.mock
    def test_successful_authentication(self, sample_api_url, sample_username, sample_password):
        token_data = make_token_response_dict()
        respx.post(f"{sample_api_url}/oauth/token").mock(return_value=httpx.Response(200, json=token_data))
        auth = SolarkAuthenticator(
            api_url=sample_api_url,
            username=sample_username,
            password=sample_password,
            timeout=10,
        )
        token = auth.authenticate()
        assert token.access_token == token_data["data"]["access_token"]
        assert token.token_type == "Bearer"

    @respx.mock
    def test_authentication_failure_raises(self, sample_api_url, sample_username, sample_password):
        respx.post(f"{sample_api_url}/oauth/token").mock(
            return_value=httpx.Response(401, json={"error": "unauthorized"})
        )
        auth = SolarkAuthenticator(
            api_url=sample_api_url,
            username=sample_username,
            password=sample_password,
            timeout=10,
        )
        with pytest.raises(httpx.HTTPStatusError):
            auth.authenticate()

    @respx.mock
    def test_api_reports_failure(self, sample_api_url, sample_username, sample_password):
        failure_response = {
            "code": 1,
            "msg": "Invalid credentials",
            "data": {
                "access_token": "",
                "token_type": "",
                "expires_in": 0,
                "refresh_token": "",
                "scope": "",
            },
            "success": False,
        }
        respx.post(f"{sample_api_url}/oauth/token").mock(return_value=httpx.Response(200, json=failure_response))
        auth = SolarkAuthenticator(
            api_url=sample_api_url,
            username=sample_username,
            password=sample_password,
            timeout=10,
        )
        with pytest.raises(RuntimeError, match="Authentication failed"):
            auth.authenticate()
