from pydantic import BaseModel
from typing import Optional


class Rentals(BaseModel):
    InquilinoName: str
    InquilinoLastName: str
    InquilinoDNI: str
    InquilinoRIF: str
    InquilinoBirthday: str
    Telefono: str
    InquilinoMail: str
    InmuebleData: str
    PriceMensual: str
    PorcentajeComision: str
    FechaDeComision: str
    FechaInicio: str
    FechaFinalizacion: str


class ContractDetails(BaseModel):
    ClienteNombre: str
    ClienteApellido: str
    PropietarioNombre: str
    PropietarioApellido: str
    InmuebleDireccion: str
    FechaInicio: str
    FechaFin: str
    ContratoID:int
    CedulaPropietario : str 
    CedulaCliente : str 
    
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