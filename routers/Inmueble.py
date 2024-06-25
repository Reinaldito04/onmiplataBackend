from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Query
from db.db import create_connection
from models.Inmuebles import Inmueble, ImageInmueble, Service, payService
from typing import List
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
        cursor.execute(
            "SELECT Nombre, Apellido, DNI FROM Propietarios WHERE ID = ?", (inmueble[3],))
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
        cursor.execute(
            "SELECT Imagen, Descripcion FROM IMAGENES WHERE InmuebleID = ?", (inmueble[0],))
        imagenes = cursor.fetchall()

        # Construir el diccionario del inmueble con toda la información obtenida
        inmueble_dist = {
            "ID": inmueble[0],
            "Direccion": inmueble[1],
            "Tipo": inmueble[2],
            "Descripcion": inmueble[4],
            "Municipio": inmueble[5],
            "NombrePropietario": nombre_propietario,
            "ApellidoPropietario": apellido_propietario,
            "CedulaPropietario": cedula_propietario,
            "NombreInquilino": cliente[0] if cliente else "No tiene inquilino",
            "ApellidoInquilino": cliente[1] if cliente else "",
            "CedulaInquilino": cliente[2] if cliente else "",
            # Lista de imágenes con su descripción
            "Imagenes": [{"Imagen": img[0], "Descripcion": img[1]} for img in imagenes]
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
        "INSERT INTO Inmuebles (Direccion, Tipo, PropietarioID,Descripcion,Municipio) VALUES (?, ?, ?,?,?)",
        (inmueble.Direccion, inmueble.Tipo,
         propietario[0], inmueble.Descripcion, inmueble.Municipio)
    )
    conn.commit()
    conn.close()
    return {
        "Message": "agregado correctamente"
    }


# SERVICIOS

@router.get("/getServices")
async def get_services(inmueble_id: int = Query(..., description="ID del inmueble")):
    conn = create_connection()
    cursor = conn.cursor()

    # Ejecuta una consulta para obtener los servicios del inmueble por su ID
    cursor.execute(
        "SELECT ID,Servicio,Proveedor,NumeroCuenta,FechaPago,Monto,Nota FROM ServiciosInmueble WHERE InmuebleID = ?", (inmueble_id,))
    services = cursor.fetchall()

    service_dist = []

    for service in services:
        service_dist.append({
            "ID": service[0],
            "Servicio": service[1],
            "Proveedor": service[2],
            "NumeroCuenta": service[3],
            "FechaPago": service[4],
            "Monto": service[5],
            "Nota": service[6]
        })

    conn.close()

    return {"services": service_dist}


@router.post("/addService")
async def add_service(service: Service):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ServiciosInmueble (Servicio, Proveedor, NumeroCuenta, FechaPago, Monto, InmuebleID, Nota) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (service.Service, service.Provider, service.nroCuenta,
         service.FechaPago, service.Monto, service.idInmueble, service.Notas)
    )
    conn.commit()
    conn.close()
    return {
        "Message": "agregado correctamente"
    }


@router.post("/addPayService")
async def pay_service(pago: payService):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO PagoServicios (Concepto,Monto,FechaPago,ContratoID,ServicioID) VALUES (?,?,?,?,?)",
            (
                pago.concepto, pago.Monto, pago.fecha, pago.contratoID, pago.servicioID
            ))
        conn.commit()
        conn.close()
        return {
            "Message": "agregado correctamente"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getServicesPays", response_model=List[dict])
async def get_services_pays():
    try:
        conn = create_connection()  # Cambia por tu conexión a la base de datos SQLite
        cursor = conn.cursor()

        # Consulta SQL para obtener todos los pagos de servicios con sus detalles
        cursor.execute("""
           SELECT 
                ps.ID AS PaymentID,
                ps.Concepto,
                ps.Monto AS MontoPago,
                ps.FechaPago,
                ps.ContratoID,
                si.ID AS ServicioID,
                si.Servicio,
                si.Proveedor,
                si.NumeroCuenta,
                si.FechaPago AS FechaServicio,
                si.Monto AS MontoServicio,
                si.InmuebleID,
                inm.ID AS InmuebleID,
                inm.Direccion AS DireccionInmueble,
                inm.Municipio AS MunicipioInmueble
            FROM 
                PagoServicios ps
            LEFT JOIN 
                ServiciosInmueble si ON ps.ServicioID = si.ID
            LEFT JOIN 
                Inmuebles inm ON si.InmuebleID = inm.ID;

            """)

        rows = cursor.fetchall()
        services_pays = []

        for row in rows:
            payment = {
                "PaymentID": row[0],
                "Concepto": row[1],
                "MontoPago": row[2],
                "FechaPago": row[3],
                "ContratoID": row[4],
                "ServicioID": row[5]
            }

            service = {
                "ServicioID": row[5],  # ServicioID
                "Servicio": row[6],
                "Proveedor": row[7],
                "NumeroCuenta": row[8],
                "FechaServicio": row[9],
                "MontoServicio": row[10],
                "InmuebleID": row[11]
            }
            Inmueble = {
                "InmuebleID": row[12],
                "Direccion": row[13],
                "Municipio": row[14]

            }
            services_pays.append({
                "Payment": payment,
                "Service": service,
                "Inmueble": Inmueble
            })

        conn.close()
        return services_pays

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getServicesToPay")
async def get_services_to_pay():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Consulta SQL para obtener los servicios por cobrar
        query = """
        SELECT 
            si.ID AS ServicioID,
            si.Servicio,
            si.Proveedor,
            si.NumeroCuenta,
            si.FechaPago AS FechaServicio,
            si.Monto AS MontoServicio,
            si.InmuebleID,
            si.Nota AS NotaServicio,
            ps.ID AS PagoID,
            ps.Concepto,
            ps.Monto AS MontoPago,
            ps.FechaPago AS FechaPago,
            c.ID AS ContratoID,
            c.ClienteID,
            c.PropietarioID,
            c.InmuebleID AS InmuebleContratoID,
            c.FechaInicio AS FechaInicioContrato,
            c.FechaFin AS FechaFinContrato,
            c.Monto AS MontoContrato,
            cli.Nombre AS NombreCliente,
            cli.Apellido AS ApellidoCliente,
            prop.Nombre AS NombrePropietario,
            prop.Apellido AS ApellidoPropietario,
            inm.Direccion AS DireccionInmueble,
            inm.Municipio AS MunicipioInmueble
        FROM 
            ServiciosInmueble si
        LEFT JOIN 
            PagoServicios ps ON si.ID = ps.ID
        LEFT JOIN 
            Contratos c ON si.InmuebleID = c.InmuebleID
        LEFT JOIN 
            Clientes cli ON c.ClienteID = cli.ID
        LEFT JOIN 
            Propietarios prop ON c.PropietarioID = prop.ID
        LEFT JOIN 
            Inmuebles inm ON si.InmuebleID = inm.ID
        WHERE 
            ps.ID IS NULL OR ps.Monto < si.Monto
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        services_to_pay = []

        for row in rows:
            service = {
                "ServicioID": row[0],
                "Servicio": row[1],
                "Proveedor": row[2],
                "NumeroCuenta": row[3],
                "FechaServicio": row[4],
                "MontoServicio": row[5],
                "InmuebleID": row[6],
                "NotaServicio": row[7]
            }
            payment = {
                "PagoID": row[8],
                "Concepto": row[9],
                "MontoPago": row[10],
                "FechaPago": row[11],
                "ContratoID": row[12]
            }
            contract = {
                "ContratoID": row[12],
                "ClienteID": row[13],
                "PropietarioID": row[14],
                "InmuebleID": row[15],
                "FechaInicioContrato": row[16],
                "FechaFinContrato": row[17],
                "MontoContrato": row[18]
            }
            client = {
                "ClienteID": row[13],
                "NombreCliente": row[19],
                "ApellidoCliente": row[20]
            }
            owner = {
                "PropietarioID": row[14],
                "NombrePropietario": row[21],
                "ApellidoPropietario": row[22]
            }
            property = {
                "InmuebleID": row[15],
                "DireccionInmueble": row[23],
                "MunicipioInmueble": row[24]
            }

            services_to_pay.append({
                "Servicio": service,
                "Pago": payment,
                "Contrato": contract,
                "Cliente": client,
                "Propietario": owner,
                "Inmueble": property
            })

        conn.close()
        return services_to_pay

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
