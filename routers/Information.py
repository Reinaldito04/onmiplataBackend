from fastapi import APIRouter,HTTPException
from db.db import create_connection
from models.Information import Acontecimiento
router = APIRouter()

@router.post("/AddAcontecimiento")
async def add_acontecimiento(acontecimiento : Acontecimiento):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Acontecimientos (ContratoID,Detalle,Fecha) VALUES (?,?,?)",
                   (acontecimiento.ContratoID, acontecimiento.Detalle, acontecimiento.Fecha))
    conn.commit()
    conn.close()
    return {
        "Message": "agregado correctamente"
    }
    
@router.get("/GetAcontecimiento/{IDContract}")
async def get_acontecimiento(IDContract: int):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Detalle, ID, Fecha FROM Acontecimientos WHERE ContratoID=?", (IDContract,))
        acontecimientos = cursor.fetchall()
        conn.close()
        
        # Convertir a una lista de diccionarios
        acontecimientos_dict = [
            {"Detalle": detalle, "ID": id, "Fecha": fecha} 
            for detalle, id, fecha in acontecimientos
        ]
        return acontecimientos_dict
    except Exception as e:
        print(e)  # Para propósitos de depuración
        raise HTTPException(status_code=500, detail="Error al obtener los acontecimientos")