from pydantic import BaseModel


class Person(BaseModel):
    name: str
    lastName: str
    dni: str
    rif: str
    email: str
    birthdate: str
    phone: str


class Propietarios (Person):
    address: str
    CodePostal: str



   
