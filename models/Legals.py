from pydantic import BaseModel

class CasoLegal(BaseModel):
    ContratoID : int 
    nombre_caso: str
    descripcion: str
    fecha_inicio: str
    fecha_fin: str
    estado: str
    
class ConceptoLegal(BaseModel):
    caso_legal_id: int
    concepto: str
    descripcion: str
    fecha: str
