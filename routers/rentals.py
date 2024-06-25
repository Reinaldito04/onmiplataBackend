from fastapi import APIRouter, HTTPException
from db.db import create_connection
from pydantic import BaseModel
from models.Rentals import Rentals, ContractDetails,ReportData,notificacionInquilino,ReporteNotificacion
from typing import List
from datetime import datetime,timedelta
from reports.Contrato import generar_reporte
from dateutil.relativedelta import relativedelta
import os
from pydantic import ValidationError
router = APIRouter()



@router.get("/contracts-expiring", response_model=List[ContractDetails])
async def get_contracts_expiring():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        current_date = datetime.now()
        start_of_month = current_date.replace(day=1)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        query = """
        SELECT 
            Clientes.Nombre AS ClienteNombre,
            Clientes.Apellido AS ClienteApellido,
            Propietarios.Nombre AS PropietarioNombre,
            Propietarios.Apellido AS PropietarioApellido,
            Inmuebles.Direccion AS InmuebleDireccion,
            Contratos.FechaInicio,
            Contratos.FechaFin,
            Contratos.ID,
            Propietarios.DNI AS PropietarioDNI,
            Clientes.DNI AS ClienteDNI,
            Contratos.DuracionMeses,
            Contratos.Monto,
            Inmuebles.Municipio,
            Clientes.Telefono,
            Inmuebles.ID
            
            
        FROM 
            Contratos
        INNER JOIN 
            Clientes ON Contratos.ClienteID = Clientes.ID
        INNER JOIN 
            Propietarios ON Contratos.PropietarioID = Propietarios.ID
        INNER JOIN 
            Inmuebles ON Contratos.InmuebleID = Inmuebles.ID
        WHERE 
            Contratos.FechaFin BETWEEN ? AND ?
        """
        
        cursor.execute(query, (start_of_month.strftime('%Y-%m-%d'), end_of_month.strftime('%Y-%m-%d')))
        result = cursor.fetchall()

        if not result:
            raise HTTPException(status_code=404, detail="No contracts expiring this month")

        contracts = []
        for row in result:
            contract = ContractDetails(
                ClienteNombre=row[0],
                ClienteApellido=row[1],
                PropietarioNombre=row[2],
                PropietarioApellido=row[3],
                InmuebleDireccion=row[4],
                FechaInicio=row[5],
                FechaFin=row[6],
                ContratoID=row[7],
                CedulaPropietario=row[8],
                CedulaCliente=row[9],
                DuracionMeses=row[10],
                Monto=row[11],
                Municipio=row[12],
                Telefono=row[13],
                InmuebleID=row[14]
            )
            contracts.append(contract)

        return contracts

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
        
        


@router.get("/contracts", response_model=List[ContractDetails])
def get_contracts():
    conn = create_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        Clientes.Nombre AS ClienteNombre,
        Clientes.Apellido AS ClienteApellido,
        Propietarios.Nombre AS PropietarioNombre,
        Propietarios.Apellido AS PropietarioApellido,
        Inmuebles.Direccion AS InmuebleDireccion,
        Contratos.FechaInicio,
        Contratos.FechaFin,
        Contratos.ID,
        Propietarios.DNI AS PropietarioDNI,
        Clientes.DNI AS ClienteDNI,
        Contratos.DuracionMeses,
        Contratos.Monto,
        Inmuebles.Municipio,
        Clientes.Telefono,
        Inmuebles.ID
        
    FROM 
        Contratos
    INNER JOIN 
        Clientes ON Contratos.ClienteID = Clientes.ID
    INNER JOIN 
        Propietarios ON Contratos.PropietarioID = Propietarios.ID
    INNER JOIN 
        Inmuebles ON Contratos.InmuebleID = Inmuebles.ID;
    """

    cursor.execute(query)
    result = cursor.fetchall()

    if not result:
        raise HTTPException(status_code=404, detail="No contracts found")

    contracts = []
    for row in result:
        contract = ContractDetails(
            ClienteNombre=row[0],
            ClienteApellido=row[1],
            PropietarioNombre=row[2],
            PropietarioApellido=row[3],
            InmuebleDireccion=row[4],
            FechaInicio=row[5],
            FechaFin=row[6],
            ContratoID = row[7],
            CedulaPropietario = row[8],
            CedulaCliente = row[9],
            DuracionMeses = row[10],
            Monto = row[11],
            Municipio = row[12],
            Telefono = row[13],
            InmuebleID=row[14]
            
            
            
        )
        contracts.append(contract)

    conn.close()
    return contracts


@router.post("/addContract")
def agg_contract(arriendo: Rentals):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        # Ejecuta la inserción
        cursor.execute(
            "INSERT INTO Clientes (Nombre, Apellido, DNI, RIF, FechaNacimiento, Telefono, Email) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (arriendo.InquilinoName, arriendo.InquilinoLastName, arriendo.InquilinoDNI,
             arriendo.InquilinoRIF, arriendo.InquilinoBirthday, arriendo.Telefono, arriendo.InquilinoMail)
        )

        # Obtén el ID de la última fila insertada
        client_id = cursor.lastrowid

        # Confirma la transacción
        conn.commit()

        # Divide el dato de InmuebleData
        cedula, direccion = arriendo.InmuebleData.split(' --- ')

        # Verifica si el propietario existe
        cursor.execute("SELECT ID FROM Propietarios WHERE DNI = ?", (cedula,))
        propietario = cursor.fetchone()
        if not propietario:
            raise HTTPException(
                status_code=404, detail="Propietario no encontrado")

        propietario_id = propietario[0]

        # Verifica si el inmueble existe
        cursor.execute(
            "SELECT ID FROM Inmuebles WHERE Direccion=? AND PropietarioID=?", (direccion, propietario_id))
        inmueble = cursor.fetchone()
        if not inmueble:
            raise HTTPException(
                status_code=404, detail="Inmueble no encontrado")

        inmueble_id = inmueble[0]

        # Calcula la duración en meses
        fecha_inicio = datetime.strptime(arriendo.FechaInicio, '%Y-%m-%d')
        fecha_fin = datetime.strptime(arriendo.FechaFinalizacion, '%Y-%m-%d')
        duracion_meses = relativedelta(fecha_fin, fecha_inicio).months + (relativedelta(fecha_fin, fecha_inicio).years * 12)

        # Inserta el contrato
        cursor.execute(
            "INSERT INTO Contratos (ClienteID, PropietarioID, InmuebleID, FechaInicio, FechaFin, Monto, Comision, FechaPrimerPago, DuracionMeses) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (client_id, propietario_id, inmueble_id, arriendo.FechaInicio, arriendo.FechaFinalizacion,
             arriendo.PriceMensual, arriendo.PorcentajeComision, arriendo.FechaDeComision, duracion_meses)
        )

        # Confirma la transacción
        conn.commit()

        return {"client_id": client_id, "message": "Cliente agregado exitosamente"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
