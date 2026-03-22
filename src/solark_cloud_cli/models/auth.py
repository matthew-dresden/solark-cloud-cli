from pydantic import BaseModel


class TokenData(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str


class TokenResponse(BaseModel):
    code: int
    msg: str
    data: TokenData
    success: bool
