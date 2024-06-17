from pydantic import BaseModel


class Pagos(BaseModel):
    Amount: float
    Date: str
    PaymentType: str
    IdContract: int


class DetailsPagos(Pagos):
    Name: str
    Lastname: str
    DNI: str
    ID : int
