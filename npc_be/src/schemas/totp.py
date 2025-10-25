# src/schemas/totp.py
from pydantic import BaseModel


class TotpVerify(BaseModel):
    login_token: str
    totp_code: str
