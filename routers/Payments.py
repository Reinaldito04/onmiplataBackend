from fastapi import APIRouter, HTTPException, Query
from db.db import create_connection
from models.Payments import DetailsPagos, Pagos, NextPayment, GestionPago
from typing import List
from datetime import datetime, timedelta
router = APIRouter()


@router.post("/gestionPays")
def pay_gestion(gestion: GestionPago):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO GestionCobro ( fechaCobro,ContratoID,Concepto) VALUES (?,?,?)",
                   (gestion.Fecha, gestion.ContratoID, gestion.Concepto))
    conn.commit()
    conn.close()
    return {
        "Message": "agregado correctamente"
    }


@router.get("/gestionPays")
def get_gestion():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   
                   SELECT gc.ID AS GestionCobroID,
                    gc.fechaCobro,
                    gc.ContratoID,
                    gc.Concepto,
                    c.ID AS ContratoID,
                    cl.ID AS ClienteID,
                    p.ID AS PropietarioID,
                    p.Nombre AS PropietarioNombre,
                    p.Apellido AS PropietarioApellido,
                    p.DNI AS PropietarioCedula ,
                    cl.Nombre AS ClienteNombre,
                    cl.Apellido AS ClienteApellido,
                    cl.DNI AS CedulaCliente
                    
                    FROM GestionCobro gc
                    JOIN 
                        Contratos c ON gc.ContratoID = c.ID
                    JOIN 
                        Clientes cl ON c.ClienteID = cl.ID
                    JOIN 
                        Propietarios p ON c.PropietarioID = p.ID;

                   
                   
                   """)
    rows = cursor.fetchall()
    conn.close()
    gestionList = []

    for row in rows:
        gestionList.append({
            "GestionCobroID": row[0],
            "FechaCobro": row[1],
            "ContratoID": row[2],
            "Concepto": row[3],
            "ContratoID": row[4],
            "ClienteID": row[5],
            "PropietarioID": row[6],
            "PropietarioNombre": row[7],
            "PropietarioApellido": row[8],
            "PropietarioCedula": row[9],
            "ClienteNombre": row[10],
            "ClienteApellido": row[11],
            "CedulaCliente": row[12],
        })
    if not gestionList:
        return []
    return gestionList


@router.get("/getPays", response_model=List[DetailsPagos])
def get_pay(type: str = Query(..., description="Tipo de pago: Empresa o Personal")):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        if type == "Empresa":
            consulta = """
            SELECT Clientes.Nombre, Clientes.Apellido, Clientes.DNI,
                   Pagos.Monto, Pagos.FechaPago, Pagos.ContratoID,Pagos.ID
            FROM Contratos
            INNER JOIN Clientes ON Contratos.ClienteID = Clientes.ID
            INNER JOIN Pagos ON Pagos.ContratoID = Contratos.ID
            WHERE Pagos.Para = 'Empresa';
            """
            payment_type = 'Empresa'
        elif type == "Personal":
            consulta = """
            SELECT Propietarios.Nombre, Propietarios.Apellido, Propietarios.DNI,
                   Pagos.Monto, Pagos.FechaPago, Pagos.ContratoID,Pagos.ID
            FROM Contratos
            INNER JOIN Propietarios ON Contratos.PropietarioID = Propietarios.ID
            INNER JOIN Pagos ON Pagos.ContratoID = Contratos.ID
            WHERE Pagos.Para = 'Personal';
            """
            payment_type = 'Personal'
        else:
            raise HTTPException(
                status_code=400, detail="Tipo de pago no válido")

        cursor.execute(consulta)
        result = cursor.fetchall()

        pagos = []
        for row in result:
            pago = DetailsPagos(
                Name=row[0],
                Lastname=row[1],
                DNI=row[2],
                Amount=row[3],
                Date=row[4],
                IdContract=row[5],
                PaymentType=payment_type,
                ID=row[6]
            )
            pagos.append(pago)

        conn.close()

        # Devuelve un array vacío si no hay resultados
        if not pagos:
            return []

        return pagos

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
# Función para obtener todos los meses entre dos fechas


@router.get("/next-payments", response_model=List[NextPayment])
def get_next_payments():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Consulta para obtener todos los contratos con su fecha de primer pago y otros detalles
        cursor.execute("""
            SELECT Contratos.ID, Contratos.FechaPrimerPago, Clientes.Nombre AS ClienteNombre, Clientes.Apellido AS ClienteApellido,
                   Inmuebles.Direccion AS InmuebleDireccion, Propietarios.Nombre AS PropietarioNombre, Propietarios.Apellido AS PropietarioApellido,
                   Contratos.Monto AS MontoContrato
            FROM Contratos
            INNER JOIN Clientes ON Contratos.ClienteID = Clientes.ID
            INNER JOIN Inmuebles ON Contratos.InmuebleID = Inmuebles.ID
            INNER JOIN Propietarios ON Contratos.PropietarioID = Propietarios.ID
        """)

        contratos = cursor.fetchall()

        if not contratos:
            raise HTTPException(status_code=404, detail="No se encontraron contratos")

        today = datetime.today()
        mes_actual = today.month
        anio_actual = today.year

        next_payments = []

        for contrato in contratos:
            contrato_id = contrato[0]
            primer_pago = datetime.strptime(contrato[1], '%Y-%m-%d')
            cliente_nombre = contrato[2]
            cliente_apellido = contrato[3]
            inmueble_direccion = contrato[4]
            propietario_nombre = contrato[5]
            propietario_apellido = contrato[6]
            monto_contrato = contrato[7]

            # Verificar si ya se registró el pago completo este mes
            cursor.execute("""
                SELECT COUNT(*) FROM ContratosPagadosMes
                WHERE ContratoID = ? AND Mes = ? AND Anio = ?
            """, (contrato_id, mes_actual, anio_actual))

            if cursor.fetchone()[0] > 0:
                continue  # Si el contrato ya está pagado este mes, lo omitimos

            # Calcular el total de los pagos realizados hasta ahora para el contrato
            cursor.execute("SELECT SUM(Monto) FROM Pagos WHERE ContratoID = ?", (contrato_id,))
            total_pagado = cursor.fetchone()[0]

            if total_pagado is None:
                total_pagado = 0

            # Calcular la deuda pendiente
            meses_transcurridos = (today.year - primer_pago.year) * 12 + (today.month - primer_pago.month)
            deuda_pendiente = (monto_contrato * meses_transcurridos) - total_pagado

            # Calcular el siguiente pago (asumiendo que los pagos son mensuales)
            siguiente_pago = primer_pago + timedelta(days=30 * meses_transcurridos)
            estado = "Deuda pendiente" if deuda_pendiente > 0 else "Pagado"

            # Crear el objeto NextPayment
            next_payment = NextPayment(
                ContratoID=contrato_id,
                PrimerPago=primer_pago.strftime('%Y-%m-%d'),
                SiguientePago=siguiente_pago.strftime('%Y-%m-%d'),
                Estado=estado,
                Monto=monto_contrato,
                ClienteNombre=cliente_nombre,
                ClienteApellido=cliente_apellido,
                PropietarioNombre=propietario_nombre,
                PropietarioApellido=propietario_apellido,
                InmuebleDireccion=inmueble_direccion,
                DeudaRestante=deuda_pendiente
            )
            next_payments.append(next_payment)

        return next_payments

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()




@router.post("/PayRental")
def pay_rental(pagos: Pagos):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Insertar el pago en la tabla de Pagos
        cursor.execute("""
            INSERT INTO Pagos (ContratoID, FechaPago, Monto, Para)
            VALUES (?, ?, ?, ?)
        """, (pagos.IdContract, pagos.Date, pagos.Amount, pagos.PaymentType))

        # Calcular el monto total del contrato y la fecha de primer pago
        cursor.execute(
            "SELECT Monto, FechaPrimerPago FROM Contratos WHERE ID = ?", (pagos.IdContract,))
        contrato = cursor.fetchone()

        if not contrato:
            raise HTTPException(
                status_code=404, detail="Contrato no encontrado")

        monto_contrato = contrato[0]
        fecha_primer_pago = datetime.strptime(contrato[1], '%Y-%m-%d')

        # Calcular el total de los pagos realizados hasta ahora para el contrato
        cursor.execute(
            "SELECT SUM(Monto) FROM Pagos WHERE ContratoID = ?", (pagos.IdContract,))
        total_pagado = cursor.fetchone()[0]

        if total_pagado is None:
            total_pagado = 0

        # Calcular la deuda pendiente
        today = datetime.today()
        meses_transcurridos = (today.year - fecha_primer_pago.year) * \
            12 + (today.month - fecha_primer_pago.month)
        deuda_pendiente = (monto_contrato * meses_transcurridos) - total_pagado

        # Verificar si se ha completado la deuda para el mes actual
        if deuda_pendiente <= 0:
            # Obtener mes y año actual
            mes_actual = today.month
            anio_actual = today.year

            # Verificar si ya se registró el pago completo este mes
            cursor.execute("""
                SELECT COUNT(*) FROM ContratosPagadosMes
                WHERE ContratoID = ? AND Mes = ? AND Anio = ?
            """, (pagos.IdContract, mes_actual, anio_actual))

            if cursor.fetchone()[0] == 0:
                # Registrar el contrato como pagado para el mes actual
                cursor.execute("""
                    INSERT INTO ContratosPagadosMes (ContratoID, Mes, Anio, FechaPagoReal)
                    VALUES (?, ?, ?, ?)
                """, (pagos.IdContract, mes_actual, anio_actual, today))

            conn.commit()
            conn.close()

            return {"message": "Pago registrado exitosamente", "status": "Pagado", "deuda_pendiente": 0}

        conn.commit()
        conn.close()

        return {"message": "Pago registrado exitosamente", "status": "Deuda pendiente", "deuda_pendiente": deuda_pendiente}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
