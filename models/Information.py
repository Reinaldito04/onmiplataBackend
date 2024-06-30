from pydantic import BaseModel


class Acontecimiento(BaseModel):
    ContratoID : int 
    Detalle : str 
    Fecha : str
    