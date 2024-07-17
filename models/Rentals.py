from pydantic import BaseModel
from typing import Optional, List, Dict


class ContratoInquilino(BaseModel):
    INQUILINO: str
    N_CONTACTO: str
    CORREO: str
    INMUEBLE: str
    FECHA_CONTRATO: str
    CANON: str
    DEPOSITO_EN_GARANTIA: str
    CANONES_MENSUALES: List[Dict[str, str]]
    TOTAL_CONTRATO: str
    DEPOSITOS_EFECTUADOS: List[Dict[str, str]]
    TOTAL_DEPOSITADO: str


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
    comisiones: List[str]


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
    Telefono: Optional[str]
    InmuebleID: Optional[int]


class ContractRenew(BaseModel):
    ID: int
    FechaInicio: str
    FechaFin: str
    Monto: float
    comisiones : List [str]

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


class Inquilino(BaseModel):
    nombre: str
    cedula: str


class Vehiculo(BaseModel):
    modelo: str
    placa: str
    color: str


class Telefono(BaseModel):
    numero: str


class ReporteNotificacion(BaseModel):
    fecha_inicio: str
    inquilinos: List[Inquilino]
    inmueble: str
    vehiculos: List[Vehiculo]
    telefonos: List[str]
    condominio: str
    ubicacion: str
    fechaActual: str

class EntregaInmueble(BaseModel):
    fechaEntrega : str 
    horaEntrega:str 
    inmueble : str 
    inquilino: str 
    cantidadLlaves: str 
    magneticas: str 
    tarjetas: str 
    controlAcceso: str 
    PinturaParedes: str 
    PuertaCloset:str 
    TechoPintura: str 
    CocinaPuerta : str 
    PinturaPuertas:str 
    cocina:str 
    limpieza: str 
    batea : str 
    lavaPlatos : str 
    cocinaEstado : str 
    pocetas : str 
    ventanas: str 
    aireacondicionado :str 
    cantv: str 
    gas : str 
    internet : str 
    corpoelec : str 
    condominio: str 
    observaciones : str 

class CrearInquilinoReporte(BaseModel):
    nombre: str
    dni: str
    telefono1: str
    email: str
    nacimiento: str
    telefono2: Optional[str]
    nombrepareja: Optional[str]
    telefonopareja: Optional[str]
    cantidadpersonas: Optional[str]
    nombrehabitante: Optional[str]
    telefonohabitante: Optional[str]
    hijos: Optional[str]
    cantidadhijos: Optional[str]
    mascotas: Optional[str]
    cantidadmacostas: Optional[str]
    tipomascota: Optional[str]
    inmueblepropietario: Optional[str]
    inmuebleunibcacion: Optional[str]
    contacto: Optional[str]
    arrendadoanteriormente: Optional[str]
    arrendadornombre: Optional[str]
    arrendadortelefono: Optional[str]
    fechadesocupacion: Optional[str]
    inmuebleubicacionanterior: Optional[str]
    causadesocupacion: Optional[str]
    religion: Optional[str]
    redes: Optional[str]
    empresanombre: Optional[str]
    economia: Optional[str]
    empresatelefono: Optional[str]
    empresamail: Optional[str]
    direccionempresa: Optional[str]
    cargo: Optional[str]
    tiempoempresa:Optional[str]
    direccionempresa :Optional[str] 
    empresapareja: Optional[str]
    empresaubicacionpareja:Optional[str]
    telefonoparejaempresa:Optional[str]
    empresaresponsable:Optional[str]
    economiaempresa:Optional[str]
    empresaresponsableubicacion:Optional[str]
    empresaresponsabletelefono:Optional[str]
    empresaresponsablemovil:Optional[str]
    empresaresponsablerif:Optional[str]
    empresaresponsablemail:Optional[str]
    respresentantelegal:Optional[str]
    dnirepresentnate:Optional[str]
    telefonorepresentante:Optional[str]   
    nombrefamiliar:Optional[str]
    cedulafamiliar: Optional[str]
    telefono1familiar:Optional[str]
    telefono2familiar:Optional[str]
    parentescofamiliar:Optional[str]
    direccionfamiliar:Optional[str]
    nombrefamiliar2:Optional[str]
    cedulafamiliar2:Optional[str]
    telefono1familiar2:Optional[str]
    telefono2familiar2:Optional[str]
    parentescofamiliar2:Optional[str]
    direccionfamiliar2:Optional[str]
    nombrenofamiliar:Optional[str]
    cedulanofamiliar:Optional[str]
    telefono1nofamiliar:Optional[str]
    telefono2nofamiliar:Optional[str]
    direccionnofamiliar:Optional[str]
    nombrenofamiliar2:Optional[str]
    cedulanofamiliar2:Optional[str]
    telefono1nofamiliar2:Optional[str]
    telefono2nofamiliar2:Optional[str]
    direccionnofamiliar2:Optional[str]
    marca:Optional[str]
    modelo:Optional[str]
    placa:Optional[str]
    color:Optional[str]
    licencia:Optional[str]