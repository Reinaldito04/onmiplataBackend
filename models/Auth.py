from pydantic import BaseModel


class LoginCredentials(BaseModel):
    username: str
    password: str


class RegisterUser(LoginCredentials):
    tipo:str