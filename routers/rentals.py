from fastapi import APIRouter, HTTPException
from db.db import create_connection

from pydantic import BaseModel
router = APIRouter()

class Rentals(BaseModel):
    InquilinoName: str
    InquilinoLastName: str
    InquilinoDNI: str
    InquilinoRIF: str
    InquilinoBirthday: str
    Telefono: str
    InquilinoMail: str
    InmuebleData : str 
    PriceMensual : str 
    PorcentajeComision : str 
    FechaDeComision:str 
    FechaInicio : str 
    FechaFinalizacion : str 
    
    
    
@router.post("/addContract")
def agg_contract(arriendo: Rentals):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Ejecuta la inserción
    cursor.execute(
        "INSERT INTO Clientes (Nombre, Apellido, DNI, RIF, FechaNacimiento, Telefono, Email) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (arriendo.InquilinoName, arriendo.InquilinoLastName, arriendo.InquilinoDNI, arriendo.InquilinoRIF, arriendo.InquilinoBirthday, arriendo.Telefono, arriendo.InquilinoMail)
    )
    
    # Obtén el ID de la última fila insertada
    client_id = cursor.lastrowid
    
    # Confirma la transacción
    conn.commit()
    cedula,direccion = arriendo.InmuebleData.split(' --- ')
    cursor.execute("SELECT ID FROM Propietarios WHERE DNI = ?",(cedula,))
    propietario = cursor.fetchone()
    
    cursor.execute("SELECT ID FROM Inmuebles WHERE Direccion=? AND PropietarioID=?",(direccion,propietario[0]))
    inmuebleID = cursor.fetchone()
    cursor.execute("INSERT INTO Contratos (ClienteID,PropietarioID,InmuebleID,FechaInicio,FechaFin,Monto,Comision,FechaPrimerPago) VALUES (?,?,?,?,?,?,?,?)",(client_id,propietario,inmuebleID,arriendo.FechaInicio,arriendo.FechaFinalizacion,arriendo.PriceMensual,arriendo.PorcentajeComision,arriendo.FechaDeComision))
    conn.commit()
    conn.close()
    
    return {"client_id": client_id, "message": "Cliente agregado exitosamente"}
    
