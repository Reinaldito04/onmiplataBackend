from pydantic import BaseModel
from typing import Optional


class Person(BaseModel):
    name: str
    lastName: str
    dni: str
    rif: Optional[str]=None
    email: str
    birthdate: str
    phone: str


class Propietarios (Person):
    address: str
    CodePostal: str



   
