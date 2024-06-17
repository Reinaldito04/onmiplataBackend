from fastapi import APIRouter, HTTPException, Query
from db.db import create_connection
from models.Payments import DetailsPagos, Pagos
from typing import List

router = APIRouter()


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

        conn.commit()
        conn.close()

        return {"message": "Pago registrado exitosamente"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
