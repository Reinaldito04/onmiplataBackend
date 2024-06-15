from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Query
from db.db import create_connection
from models.Inmuebles import Inmueble, ImageInmueble
from pathlib import Path
from datetime import datetime
import uuid

import os
import shutil


router = APIRouter()

# ImagenEndpoint
MEDIA_DIRECTORY = "./media"





class ImageInmueble:
    def __init__(self, idInmueble: int, descripcion: str):
        self.idInmueble = idInmueble
        self.descripcion = descripcion


@router.post("/addImagen")
async def add_imagen(idInmueble: int = Form(...), descripcion: str = Form(...), file: UploadFile = File(...)):
    try:
        # Procesar la imagen y los datos de ImageInmueble
        image_inmueble = ImageInmueble(
            idInmueble=idInmueble, descripcion=descripcion)

        # Crear un nombre de archivo único
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(MEDIA_DIRECTORY, unique_filename)

        # Guardar la imagen en el directorio de medios
        with open(file_path, "wb") as image_file:
            image_file.write(await file.read())
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Imagenes (Descripcion,InmuebleID,Imagen,FechaSubida) VALUES(?,?,?,?)",
                       (image_inmueble.descripcion, image_inmueble.idInmueble, unique_filename, datetime.now()))
        conn.commit()
        conn.close()
        # Aquí puedes hacer cualquier procesamiento adicional con la imagen guardada

        return {
            "id": image_inmueble.idInmueble,
            "descripcion": image_inmueble.descripcion,
            "imagen": unique_filename  # Devuelve el nombre del archivo único
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_unique_filename(original_filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:6]  # Genera un UUID único de 6 caracteres
    _, file_extension = os.path.splitext(original_filename)
    return f"{timestamp}_{unique_id}{file_extension}"
# InmueblesEndPoint

@router.get("/getInmuebles")
async def get_inmuebles():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Inmuebles")
    inmuebles = cursor.fetchall()

    inmuebles_list = []
    for inmueble in inmuebles:
        # Obtener información del propietario del inmueble
        cursor.execute("SELECT Nombre, Apellido, DNI FROM Propietarios WHERE ID = ?", (inmueble[3],))
        propietario = cursor.fetchone()

        nombre_propietario = propietario[0] if propietario else ""
        apellido_propietario = propietario[1] if propietario else ""
        cedula_propietario = propietario[2] if propietario else ""

        # Obtener información del inquilino (cliente) si existe contrato asociado al inmueble
        cursor.execute("""
            SELECT 
                Clientes.Nombre AS ClienteNombre,
                Clientes.Apellido AS ClienteApellido,
                Clientes.DNI AS ClienteDNI
            FROM 
                Contratos
            INNER JOIN 
                Clientes ON Contratos.ClienteID = Clientes.ID
            WHERE
                Contratos.InmuebleID = ?
        """, (inmueble[0],))  # Asumo que inmueble[0] es el ID de Inmuebles

        cliente = cursor.fetchone()

        # Obtener las imágenes asociadas al inmueble
        cursor.execute("SELECT Imagen, Descripcion FROM IMAGENES WHERE InmuebleID = ?", (inmueble[0],))
        imagenes = cursor.fetchall()

        # Construir el diccionario del inmueble con toda la información obtenida
        inmueble_dist = {
            "ID": inmueble[0],
            "Direccion": inmueble[1],
            "Tipo": inmueble[2],
            "NombrePropietario": nombre_propietario,
            "ApellidoPropietario": apellido_propietario,
            "CedulaPropietario": cedula_propietario,
            "NombreInquilino": cliente[0] if cliente else "No tiene inquilino",
            "ApellidoInquilino": cliente[1] if cliente else "",
            "CedulaInquilino": cliente[2] if cliente else "",
            "Imagenes": [{"Imagen": img[0], "Descripcion": img[1]} for img in imagenes]  # Lista de imágenes con su descripción
        }
        inmuebles_list.append(inmueble_dist)

    conn.close()
    return inmuebles_list



@router.post("/addInmueble")
async def add_inmueble(inmueble: Inmueble):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ID FROM Propietarios WHERE DNI=?",
                   (inmueble.CedulaPropietario,))
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
        "Message": "agregado correctamente"
    }
