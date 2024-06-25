from pydantic import BaseModel


class Inmueble(BaseModel):
    Direccion: str
    Tipo: str
    CedulaPropietario: str
    Descripcion: str
    Municipio : str 


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
    
class payService(BaseModel):
    fecha: str 
    Monto : float 
    servicioID : int
    contratoID : int  
    concepto : str 