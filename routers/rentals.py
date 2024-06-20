from fastapi import APIRouter, HTTPException
from db.db import create_connection
from pydantic import BaseModel
from models.Rentals import Rentals, ContractDetails,ReportData,notificacionInquilino
from typing import List
from datetime import datetime,timedelta
from reports.Contrato import generar_reporte
from dateutil.relativedelta import relativedelta
import os
from pydantic import ValidationError
router = APIRouter()

@router.post("/generate-notificacionInquilino")
def generate_inquilino(notificacion: notificacionInquilino):
    try:
        # Validar los datos recibidos antes de continuar
        

        template_path = 'reports/documents/plantillaInquilino.docx'
        output_base_path = 'reports/output'

        # Asegurarse de que el directorio de salida existe
        if not os.path.exists(output_base_path):
            os.makedirs(output_base_path)

        # Generar el reporte
        nombre_archivo = generar_reporte(template_path=template_path, output_base_path=output_base_path, variables=notificacion.model_dump(),tipo="Notificacion")

        return {"message": "Reporte generado exitosamente", "file_path": nombre_archivo}
    
    except HTTPException as http_error:
        # Capturar errores de validación HTTP (por ejemplo, 422 Unprocessable Entity)
        raise http_error
    
    except ValidationError as validation_error:
        # Capturar errores de validación de Pydantic (por ejemplo, campos faltantes o incorrectos)
        raise HTTPException(status_code=422, detail=f"Error de validación de datos: {str(validation_error)}")
    
    except Exception as e:
        # Capturar cualquier otro error inesperado
        error_message = f"Error generando el reporte: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)


@router.post("/generate-contratReport")
def generate_report(report_data: ReportData):
    try:
        # Validar los datos recibidos antes de continuar
        validate_report_data(report_data)

        template_path = 'reports/documents/contratoplantilla.docx'
        output_base_path = 'reports/output'

        # Asegurarse de que el directorio de salida existe
        if not os.path.exists(output_base_path):
            os.makedirs(output_base_path)

        # Generar el reporte
        nombre_archivo = generar_reporte(template_path, output_base_path, report_data.model_dump(),"reporte")

        return {"message": "Reporte generado exitosamente", "file_path": nombre_archivo}
    
    except HTTPException as http_error:
        # Capturar errores de validación HTTP (por ejemplo, 422 Unprocessable Entity)
        raise http_error
    
    except ValidationError as validation_error:
        # Capturar errores de validación de Pydantic (por ejemplo, campos faltantes o incorrectos)
        raise HTTPException(status_code=422, detail=f"Error de validación de datos: {str(validation_error)}")
    
    except Exception as e:
        # Capturar cualquier otro error inesperado
        error_message = f"Error generando el reporte: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)

def validate_report_data(report_data: ReportData):
    # Validar que todos los campos obligatorios estén presentes y en el formato correcto
    if not report_data.fecha:
        raise HTTPException(status_code=422, detail="Falta la fecha en los datos del reporte")
    
    if not report_data.nombre:
        raise HTTPException(status_code=422, detail="Falta el nombre en los datos del reporte")
    
    if not report_data.inmueble:
        raise HTTPException(status_code=422, detail="Falta el inmueble en los datos del reporte")
    
    if not report_data.municipio:
        raise HTTPException(status_code=422, detail="Falta el municipio en los datos del reporte")
    
    if not report_data.motivo:
        raise HTTPException(status_code=422, detail="Falta el motivo en los datos del reporte")
    
    if not report_data.fechaInicio:
        raise HTTPException(status_code=422, detail="Falta la fecha de inicio en los datos del reporte")
    else:
        try:
            # Validar que la fecha de inicio esté en el formato correcto (YYYY-MM-DD)
            datetime.strptime(report_data.fechaInicio, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=422, detail="Formato incorrecto para la fecha de inicio. Debe ser YYYY-MM-DD")
    
    if not report_data.fechaFin:
        raise HTTPException(status_code=422, detail="Falta la fecha de fin en los datos del reporte")
    else:
        try:
            # Validar que la fecha de fin esté en el formato correcto (YYYY-MM-DD)
            datetime.strptime(report_data.fechaFin, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=422, detail="Formato incorrecto para la fecha de fin. Debe ser YYYY-MM-DD")
    
    if not report_data.duracionMeses:
        raise HTTPException(status_code=422, detail="Falta la duración en meses en los datos del reporte")
    else:
        try:
            # Validar que la duración en meses sea un número entero positivo
            duracion_meses = int(report_data.duracionMeses)
            if duracion_meses <= 0:
                raise ValueError
        except ValueError:
            raise HTTPException(status_code=422, detail="La duración en meses debe ser un número entero positivo")
    
    if not report_data.monto:
        raise HTTPException(status_code=422, detail="Falta el monto en los datos del reporte")
    else:
        try:
            # Validar que el monto sea un número decimal positivo
            monto = float(report_data.monto)
            if monto <= 0:
                raise ValueError
        except ValueError:
            raise HTTPException(status_code=422, detail="El monto debe ser un número decimal positivo")
        
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
            Inmuebles.Municipio
            
            
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
                Municipio=row[12]
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
        Inmuebles.Municipio
        
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
            Municipio = row[12]
            
            
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
