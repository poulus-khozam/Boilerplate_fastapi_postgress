from pydantic import BaseModel


class UserLogin(BaseModel):
    id_number: str
    password: str
