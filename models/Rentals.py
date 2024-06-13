from pydantic import BaseModel


class Rentals(BaseModel):
    InquilinoName:str 
    InquilinoLastName:str
    InquilinoDNI:str 
    InquilinoRIF : str 
    InquilinoMail : str 
    Telefono : str 
    InquilinoBirthday:str
    InmuebleData : str
    Price : str 
    Porcentaje: str 
    PagoComision:str 
    FechaInicio : str 
    FechaFinalizacion : str 