from fastapi import APIRouter, File, UploadFile, HTTPException, Query,Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import sqlite3
import os
import datetime
from models.Legals import CasoLegal, ConceptoLegal
from db.db import create_connection
from datetime import date


router = APIRouter()


def save_file(file: UploadFile, directory: str) -> str:
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    return file_path


@router.get("/casos-legales/")
async def get_casos_legales(contrato_id: int = Query(None)):
    conn = create_connection()
    cursor = conn.cursor()

    if contrato_id:
        cursor.execute(
            "SELECT * FROM CasosLegales WHERE ContratoID = ?", (contrato_id,))
    else:
        cursor.execute("SELECT * FROM CasosLegales")

    rows = cursor.fetchall()
    conn.close()

    casos_legales = []
    for row in rows:
        caso = {
            "id": row[0],
            "contrato_id": row[1],
            "nombre_caso": row[2],
            "descripcion": row[3],
            "fecha_inicio": row[4],
            "fecha_fin": row[5],
            "estado": row[6]
        }

        casos_legales.append(caso)

    return casos_legales


@router.get("/conceptos-legales/", )
def get_conceptos_legales(caso_legal_id: int = Query(None)):
    conn = create_connection()
    cursor = conn.cursor()

    if caso_legal_id:
        cursor.execute(
            "SELECT * FROM ConceptosLegales WHERE CasoLegalID = ?", (caso_legal_id,))
    else:
        cursor.execute("SELECT * FROM ConceptosLegales")

    conceptos_legales = cursor.fetchall()
    conn.close()
    conceptos = []

    for concepto in conceptos_legales:
        concepto = {
            "id": concepto[0],
            "caso_legal_id": concepto[1],
            "concepto": concepto[2],
            "descripcion": concepto[3],
            "fecha": concepto[4]
        }
        conceptos.append(concepto)

    return conceptos


@router.get("/casos-legales")
async def obtener_casolega():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM CasosLegales")
    rows = cursor.fetchall()
    conn.close()
    casos = []
    for row in rows:
        caso = {
            "id": row[0],
            "contrato_id": row[1],
            "nombre_caso": row[2],
            "descripcion": row[3],
            "fecha_inicio": row[4],
            "fecha_fin": row[5],
            "estado": row[6]
        }
        casos.append(caso)
    return casos


@router.delete("/casos-legales-Delete/{ID}")
def eliminar_caso_legal(ID: int):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM CasosLegales WHERE ID =?", (ID,))
    cursor.execute("DELETE FROM ConceptosLegales WHERE CasoLegalID =?", (ID,))
    conn.commit()
    conn.close()
    return {
        "message": "Caso legal eliminado"
    }


@router.post("/casos-legales/")
def crear_caso_legal(caso: CasoLegal):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO CasosLegales (ContratoID, NombreCaso, Descripcion, FechaInicio, FechaFin, Estado)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (caso.ContratoID, caso.nombre_caso, caso.descripcion, caso.fecha_inicio, caso.fecha_fin, caso.estado))
    conn.commit()
    caso_id = cursor.lastrowid
    conn.close()
    return {"id": caso_id}


@router.post("/conceptos-legales/")
def crear_concepto_legal(concepto: ConceptoLegal):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ConceptosLegales (CasoLegalID, Concepto, Descripcion, Fecha)
        VALUES (?, ?, ?, ?)
    """, (concepto.caso_legal_id, concepto.concepto, concepto.descripcion, concepto.fecha))
    conn.commit()
    concepto_id = cursor.lastrowid
    conn.close()
    return {"id": concepto_id}

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@router.get("/getDocumentsLegals")
async def obtenerDocumentos():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM DocumentosLegales")
    rows = cursor.fetchall()
    conn.close()
    docs = []
    for row in rows:
        doc = {
            "id": row[0],
            "caso_legal_id": row[1],
            "nombre": row[2],
            "ruta_archivo": row[3],
            "fecha_subida": row[4]
            
        }
        docs.append(doc)
    return docs

@router.post("/upload/")
async def upload_file(
    casoID: int = Form(...),
    nombre: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        file_location = os.path.join(UPLOAD_FOLDER, file.filename)
        
        # Guardar el archivo en la carpeta
        with open(file_location, "wb") as f:
            f.write(await file.read())
        
        # Insertar la información del archivo en la base de datos
        conn = create_connection()
        cursor = conn.cursor()
        fecha = datetime.datetime.now().isoformat()  # Capturar la fecha actual en formato ISO
        cursor.execute("INSERT INTO DocumentosLegales (CasoLegalID, NombreDocumento, RutaArchivo, FechaSubida) VALUES (?, ?, ?, ?)",
                       (casoID, nombre, file_location, fecha))
        conn.commit()
        conn.close()
        
        # Devolver la ruta del archivo en la respuesta
        return JSONResponse(status_code=200, content={
            "message": "Archivo subido exitosamente",
            "filename": file.filename,
            "file_path": file_location
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})