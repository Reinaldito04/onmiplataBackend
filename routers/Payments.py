from fastapi import APIRouter, HTTPException, Query
from db.db import create_connection
from models.Payments import DetailsPagos, Pagos, NextPayment, GestionPago
from typing import List
from datetime import datetime, timedelta
router = APIRouter()


@router.delete('/deletePay/{id}')
def delete_pay(id: int):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Pagos WHERE ID =?", (id,))
    conn.commit()
    conn.close()
    return {
        "message": "Payment deleted successfully"
    }
    

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
        date_obj = datetime.strptime(row[1], '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d/%m/%Y')
        gestionList.append({
            "GestionCobroID": row[0],
            "FechaCobro": formatted_date,
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


@router.get('/getPaysInquilino/{id}')
def get_paysInquilinos(id: int):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Suponiendo que hay una relación entre Inquilino y Pagos a través de un Contrato.
    cursor.execute("""
        SELECT p.ID,p.ContratoID,p.FechaPago,p.Monto, p.Para,p.TipoPago,p.Metodo
        from Pagos p 
        inner join Contratos c on p.ContratoID = c.ID
        where c.ClienteID = ?
    """, (id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    paymentList = []

    for row in rows:
        date_obj = datetime.strptime(row[2], '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d/%m/%Y')
        paymentList.append({
            "ID": row[0],
            "ContratoID": row[1],
            "Fecha": formatted_date,
            "Monto": row[3],
            "Para": row[4],
            "TipoPago": row[5],
            "Metodo": row[6]
        })
    
    if not paymentList:
        raise HTTPException(status_code=404, detail="No payments found for this tenant.")
    else :
        return paymentList
    
@router.get("/getPays/{id}")
def get_paysIndividual(id : int):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Pagos WHERE ContratoID = ?", (id,))
    rows = cursor.fetchall()
    conn.close()
    paymentList = []
    

    for row in rows:
        date_obj = datetime.strptime(row[2], '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d/%m/%Y')
        paymentList.append({
            "ID": row[0],
            "ContratoID": row[1],
            "Fecha": formatted_date,
            "Monto": row[3],
            "Para": row[4],
            "TipoPago": row[5],
            "Metodo": row[6]
        })
    if not paymentList:
        return []
    return paymentList

@router.get('/getPaysGaranty')
def get_paysGaranty():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Clientes.Nombre, Clientes.Apellido, Clientes.DNI,Propietarios.Nombre,Propietarios.Apellido,Propietarios.DNI,
                   Pagos.Monto, Pagos.FechaPago, Pagos.ContratoID,Pagos.ID,Pagos.TipoPago,Pagos.Metodo
            FROM Contratos
            INNER JOIN Clientes ON Contratos.ClienteID = Clientes.ID
			INNER JOIN Propietarios on Contratos.PropietarioID = Propietarios.ID
            INNER JOIN Pagos ON Pagos.ContratoID = Contratos.ID WHERE TipoPago = 'Deposito De Garantia';
    """, )
    result = cursor.fetchall()
    conn.close()

    if not result:
        raise HTTPException(status_code=404, detail="No payments found for this tenant.")
    pagos = []
    for row in result :
        date_obj = datetime.strptime(row[7], '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d/%m/%Y')
        pago = {
            "ClienteNombre": row[0],
            "ClienteApellido": row[1],
            "ClienteDNI" : row[2],
            "PropietarioNombre": row[3],
            "PropietarioApellido": row[4],
            "PropietarioDNI": row[5],
            "Monto": row[6],
            "Fecha": formatted_date,
            "IDContrato": row[8],
            "ID": row[9],
            "TipoPago": row[10],
            "Metodo": row[11]
        }
        pagos.append(pago)
    if not pagos :
        return []
    return pagos
        

    

@router.get("/getPays", response_model=List[DetailsPagos])
def get_pay(type: str = Query(..., description="Tipo de pago: Empresa o Personal")):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        if type == "Empresa":
            consulta = """
            SELECT Clientes.Nombre, Clientes.Apellido, Clientes.DNI,
                   Pagos.Monto, Pagos.FechaPago, Pagos.ContratoID,Pagos.ID,Pagos.TipoPago,Pagos.Metodo
            FROM Contratos
            INNER JOIN Clientes ON Contratos.ClienteID = Clientes.ID
            INNER JOIN Pagos ON Pagos.ContratoID = Contratos.ID
            WHERE Pagos.Para = 'Empresa';
            """
            payment_type = 'Empresa'
        elif type == "Personal":
            consulta = """
            SELECT Propietarios.Nombre, Propietarios.Apellido, Propietarios.DNI,
                   Pagos.Monto, Pagos.FechaPago, Pagos.ContratoID,Pagos.ID,Pagos.TipoPago,Pagos.Metodo
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
            
            date_obj = datetime.strptime(row[4], '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d/%m/%Y')
            pago = DetailsPagos(
                Name=row[0],
                Lastname=row[1],
                DNI=row[2],
                Amount=row[3],
                Date=formatted_date,
                IdContract=row[5],
                PaymentType=payment_type,
                ID=row[6],
                TypePay=row[7],
                PaymentMethod=row[8]
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
            date_obj = datetime.strptime(primer_pago, '%Y-%m-%d')
            date_objSegundo = datetime.strptime(siguiente_pago,'%Y-%m-%d')
            formatted_date = date_objSegundo.strftime('%d/%m/%Y')
            formatedd_dateSegundo =date_objSegundo.strftime('%d/%m/%Y')
            # Crear el objeto NextPayment
            next_payment = NextPayment(
                ContratoID=contrato_id,
                PrimerPago=formatted_date,
                SiguientePago=formatedd_dateSegundo,
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



@router.get("/getPendingPayments")
def get_pending_payments():
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                C.ID AS ContratoID,
                C.Monto AS MontoContrato,
                CL.ID AS ClienteID,
                CL.Nombre AS ClienteNombre,
                CL.Apellido AS ClienteApellido,
                CL.DNI AS ClienteDNI,
                COALESCE(SUM(PG.Monto), 0) AS TotalPagado,
                C.FechaPrimerPago AS FechaPrimerPago,
                C.FechaFin AS FechaVencimiento,
                I.Direccion AS InmuebleDireccion,
                PR.Nombre AS PropietarioNombre,
                PR.Apellido AS PropietarioApellido
            FROM 
                Contratos C
            LEFT JOIN 
                Pagos PG ON C.ID = PG.ContratoID AND PG.TipoPago = 'Arrendamiento'
            INNER JOIN 
                Clientes CL ON C.ClienteID = CL.ID
            INNER JOIN 
                Inmuebles I ON C.InmuebleID = I.ID
            INNER JOIN 
                Propietarios PR ON C.PropietarioID = PR.ID
            WHERE 
                C.Estado = 'Activo'
            GROUP BY 
                C.ID, CL.ID, I.ID, PR.ID
            HAVING 
                ((strftime('%Y', 'now') - strftime('%Y', C.FechaPrimerPago)) * 12 
                + (strftime('%m', 'now') - strftime('%m', C.FechaPrimerPago))) > 0
                AND (C.Monto * ((strftime('%Y', 'now') - strftime('%Y', C.FechaPrimerPago)) * 12 
                + (strftime('%m', 'now') - strftime('%m', C.FechaPrimerPago)))) > COALESCE(SUM(PG.Monto), 0)
        """)

        deudas = cursor.fetchall()

        if not deudas:
            return {"message": "No hay pagos pendientes de deuda"}

        response = []
        for deuda in deudas:
            contrato_id = deuda[0]
            monto_contrato = deuda[1]
            cliente_id = deuda[2]
            cliente_nombre = deuda[3]
            cliente_apellido = deuda[4]
            cliente_dni = deuda[5]
            total_pagado = deuda[6]
            fecha_primer_pago = deuda[7]
            fecha_vencimiento = deuda[8]
            inmueble_direccion = deuda[9]
            propietario_nombre = deuda[10]
            propietario_apellido = deuda[11]

            # Convertir la fecha de primer pago a un objeto datetime
            fecha_primer_pago_dt = datetime.strptime(fecha_primer_pago, '%Y-%m-%d')
            
            # Extraer el día del primer pago
            dia_primer_pago = fecha_primer_pago_dt.day

            # Calcular meses transcurridos desde el primer pago
            meses_transcurridos = (datetime.today().year - fecha_primer_pago_dt.year) * 12 + (datetime.today().month - fecha_primer_pago_dt.month)

            # Calcular la deuda pendiente
            deuda_pendiente = (monto_contrato * meses_transcurridos) - total_pagado

            if deuda_pendiente > 0:
                response.append({
                    "ContratoID": contrato_id,
                    "ClienteID": cliente_id,
                    "ClienteNombre": cliente_nombre,
                    "ClienteApellido": cliente_apellido,
                    "ClienteDNI": cliente_dni,
                    "MontoContrato": monto_contrato,
                    "TotalPagado": total_pagado,
                    "DeudaPendiente": deuda_pendiente,
                    "FechaPrimerPago": fecha_primer_pago,
                    "DiaPrimerPago": dia_primer_pago,  # Agregar el día del primer pago a la respuesta
                    "FechaVencimiento": fecha_vencimiento,
                    "InmuebleDireccion": inmueble_direccion,
                    "PropietarioNombre": propietario_nombre,
                    "PropietarioApellido": propietario_apellido
                })

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
@router.post("/PayRental")
def pay_rental(pagos: Pagos):
    
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Pagos (ContratoID, FechaPago, Monto, Para,TipoPago,Metodo)
            VALUES (?, ?, ?, ?,?,?)
        """, (pagos.IdContract, pagos.Date, pagos.Amount, pagos.PaymentType,pagos.TypePay,pagos.PaymentMethod))

        # Calcular el monto total del contrato y la fecha de primer pago
        if (pagos.TypePay == 'Arrendamiento'):
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
                "SELECT SUM(Monto) FROM Pagos WHERE ContratoID = ? AND TipoPago=?", (pagos.IdContract,pagos.TypePay))
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
        else:
            conn.commit()
            conn.close()
            return {"message": "Pago registrado exitosamente"}
        

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
