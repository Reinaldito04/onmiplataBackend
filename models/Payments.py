from pydantic import BaseModel
from typing import Optional

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

class NextPayment(BaseModel):
    ContratoID: int
    PrimerPago: str
    SiguientePago: str
    Estado: str
    Monto: Optional[float]
    ContratoID: int
    PrimerPago: str
    SiguientePago: str
    ClienteNombre:str
    ClienteApellido:str
    PropietarioNombre:str
    PropietarioApellido:str
    InmuebleDireccion : str 
    DeudaRestante: float
    
class GestionPago(BaseModel):
    ContratoID: int
    Fecha : str 
    Concepto : str 