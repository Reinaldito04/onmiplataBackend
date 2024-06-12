from fastapi import APIRouter,HTTPException
from db.db import create_connection
from models.Inmuebles import Inmueble
router = APIRouter()


@router.post("/addInmueble")
async def  add_inmueble(inmueble : Inmueble,cedulaPropietario):
    conn =create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ID FROM Propietarios WHERE DNI=?", (cedulaPropietario,))
    propietario = cursor.fetchone()

    if not propietario:
        raise HTTPException(status_code=404, detail="Propietario not found")
    
    cursor.execute(
        "INSERT INTO Inmuebles (Direccion, Tipo, PropietarioID) VALUES (?, ?, ?)",
        (inmueble.Direccion, inmueble.Tipo, propietario[0])
    )
    conn.commit()
    conn.close()
    