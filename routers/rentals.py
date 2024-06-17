from fastapi import APIRouter, HTTPException
from db.db import create_connection
from pydantic import BaseModel
from models.Rentals import Rentals, ContractDetails,NextPayment
from typing import List
from datetime import datetime,timedelta

router = APIRouter()


@router.get("/next-payments", response_model=List[NextPayment])
def get_next_payments():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Consulta para obtener todos los contratos con su fecha de primer pago
        cursor.execute("""
            SELECT Contratos.ID, Contratos.FechaPrimerPago, Clientes.Nombre AS ClienteNombre, Clientes.Apellido AS ClienteApellido,
                   Inmuebles.Direccion AS InmuebleDireccion, Propietarios.Nombre AS PropietarioNombre,
                   Pagos.FechaPago AS UltimoPago, Pagos.Monto AS MontoUltimoPago
            FROM Contratos
            INNER JOIN Clientes ON Contratos.ClienteID = Clientes.ID
            INNER JOIN Inmuebles ON Contratos.InmuebleID = Inmuebles.ID
            INNER JOIN Propietarios ON Contratos.PropietarioID = Propietarios.ID
            LEFT JOIN Pagos ON Pagos.ContratoID = Contratos.ID 
            """)

        contratos = cursor.fetchall()

        if not contratos:
            raise HTTPException(status_code=404, detail="No se encontraron contratos")

        today = datetime.today()

        next_payments = []
        for contrato in contratos:
            contrato_id = contrato[0]
            primer_pago = datetime.strptime(contrato[1], '%Y-%m-%d')

            # Calcula el siguiente pago a partir del mes del primer pago
            siguiente_pago = primer_pago
            while siguiente_pago <= today:
                siguiente_pago += timedelta(days=30)  # Suponiendo pagos mensuales
            
            # Verifica si hay un pago registrado para esta fecha
            if contrato[6]:  # Si hay un último pago registrado
                estado = "Pagado"
                monto = contrato[7]
            else:
                if siguiente_pago > today:
                    estado = "Pendiente"
                    monto = None
                else:
                    estado = "Vencido"
                    monto = None
            
            # Guarda el resultado en la lista de próximos pagos
            next_payment = NextPayment(
                ContratoID=contrato_id,
                ClienteNombre=contrato[2],
                ClienteApellido=contrato[3],
                InmuebleDireccion=contrato[4],
                PropietarioNombre=contrato[5],
                PrimerPago=primer_pago.strftime('%Y-%m-%d'),
                SiguientePago=siguiente_pago.strftime('%Y-%m-%d'),
                Estado=estado,
                Monto=monto
            )
            next_payments.append(next_payment)

        return next_payments

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
        Clientes.DNI AS ClienteDNI
        
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
            CedulaCliente = row[9]
            
            
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

        # Inserta el contrato
        cursor.execute(
            "INSERT INTO Contratos (ClienteID, PropietarioID, InmuebleID, FechaInicio, FechaFin, Monto, Comision, FechaPrimerPago) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (client_id, propietario_id, inmueble_id, arriendo.FechaInicio, arriendo.FechaFinalizacion,
             arriendo.PriceMensual, arriendo.PorcentajeComision, arriendo.FechaDeComision)
        )

        # Confirma la transacción
        conn.commit()

        return {"client_id": client_id, "message": "Cliente agregado exitosamente"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
