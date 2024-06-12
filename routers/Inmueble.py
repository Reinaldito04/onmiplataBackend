from fastapi import APIRouter,HTTPException
from db.db import create_connection
from models.Inmuebles import Inmueble
router = APIRouter()


@router.get("/getInmuebles")
async def get_inmuebles():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Inmuebles")
    inmuebles = cursor.fetchall()
  
    
    inmuebles_list =[]
    for inmueble in inmuebles:
        cursor.execute("SELECT Nombre, Apellido FROM Propietarios WHERE ID = ?", (inmueble[3],))
        propietario = cursor.fetchone()
        
        nombrePropietario = propietario[0]
        apellidoPropietario = propietario[1]
        
        
        
        inmuebles_dist={
            "ID":inmueble[0],
            "Direccion":inmueble[1],
            "Tipo": inmueble[2],
            "NombrePropietario": nombrePropietario,
            "ApellidoPropietario":apellidoPropietario
        }
        inmuebles_list.append(inmuebles_dist)
        
    conn.close()
    return inmuebles_list
    
@router.post("/addInmueble")
async def  add_inmueble(inmueble : Inmueble) :
    conn =create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ID FROM Propietarios WHERE DNI=?", (inmueble.CedulaPropietario,))
    propietario = cursor.fetchone()

    if not propietario:
        raise HTTPException(status_code=404, detail="Propietario not found")
    
    cursor.execute(
        "INSERT INTO Inmuebles (Direccion, Tipo, PropietarioID) VALUES (?, ?, ?)",
        (inmueble.Direccion, inmueble.Tipo, propietario[0])
    )
    conn.commit()
    conn.close()
    return {
        "Message":"agregado correctamente"
    }
    