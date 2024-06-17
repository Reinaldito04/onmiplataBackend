from pydantic import BaseModel


class Inmueble(BaseModel):
    Direccion: str
    Tipo: str
    CedulaPropietario: str
    Descripcion: str


class ImageInmueble(BaseModel):
    idInmueble: str
    descripcion: str
