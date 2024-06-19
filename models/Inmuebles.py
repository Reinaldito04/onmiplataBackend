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
