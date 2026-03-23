import logging
from typing import Protocol

import httpx

from solark_cloud_cli.models.auth import TokenData, TokenResponse

logger = logging.getLogger(__name__)


class Authenticator(Protocol):
    def authenticate(self) -> TokenData: ...


class SolarkAuthenticator:
    _CLIENT_ID = "csp-web"
    _GRANT_TYPE = "password"

    def __init__(self, api_url: str, username: str, password: str, timeout: int) -> None:
        self._api_url = api_url.rstrip("/")
        self._username = username
        self._password = password
        self._timeout = timeout

    def authenticate(self) -> TokenData:
        url = f"{self._api_url}/oauth/token"
        logger.info("Authenticating with SolarkCloud API")
        logger.debug("Auth request to %s", url)
        payload = {
            "client_id": self._CLIENT_ID,
            "grant_type": self._GRANT_TYPE,
            "username": self._username,
            "password": self._password,
        }
        response = httpx.post(
            url,
            json=payload,
            headers={
                "Content-Type": "application/json;charset=UTF-8",
                "Origin": "https://www.solarkcloud.com",
                "Referer": "https://www.solarkcloud.com/",
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        token_response = TokenResponse.model_validate(response.json())
        if not token_response.success:
            msg = f"Authentication failed: {token_response.msg}"
            raise RuntimeError(msg)
        logger.info("Authentication successful")
        return token_response.data
