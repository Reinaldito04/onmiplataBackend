from pydantic import BaseModel

class Inmueble(BaseModel):
    Direccion : str
    Tipo : str 
    CedulaPropietario:str
  