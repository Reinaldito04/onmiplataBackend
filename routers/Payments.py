from fastapi import APIRouter,HTTPException
from db.db import create_connection
from models.Payments import Pagos

router = APIRouter()
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
    
