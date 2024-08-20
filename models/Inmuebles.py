from pydantic import BaseModel
from typing import Optional

class Inmueble(BaseModel):
    Direccion: str
    Tipo: str
    CedulaPropietario: Optional[str]
    Descripcion: str
    Municipio : str 
    Estacionamiento : str 


class ImageInmueble(BaseModel):
    idInmueble: str
    descripcion: str


class Service(BaseModel):
    idInmueble: int
    Service : str 
    Provider : str 
    nroCuenta: str 
    FechaPago : str 
    Monto : float 
    Notas : str 
    
    
class Corpoelec(BaseModel):
    idInmueble : int
    NIC : str 
    usuario : str 
    password : str
    CorreoPassword : str 
     
class payService(BaseModel):
    fecha: str 
    Monto : float 
    servicioID : int
    contratoID : int  
    concepto : str 