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
    ContratoID: int
    CedulaPropietario: str
    CedulaCliente: str
    DuracionMeses: int
    Monto: float
    Municipio: str


class ReportData(BaseModel):
    fecha: str
    nombre: str
    inmueble: str
    municipio: str
    motivo: str
    fechaInicio: str
    fechaFin: str
    duracionMeses: int
    monto: float


class notificacionInquilino(BaseModel):
    condominio: str
    fecha: str
    nombre: str
    cedula: str
    inmueble: str
    telefono: str
    mes: str
    year: str
    mudanzaday: str
    mudanzames: str
