from pydantic import BaseModel


class registerInformation(BaseModel):
    username: str
    description: str 


class LoginCredentials(BaseModel):
    username: str
    password: str


class RegisterUser(LoginCredentials):
    tipo:str