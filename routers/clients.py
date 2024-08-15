from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from db.db import create_connection
from models.Clients import Propietarios, Person
from datetime import datetime
import os
import uuid

router = APIRouter()

# Cumpleaños


@router.get("/getBirthdays")
async def get_birthdays():
    conn = create_connection()
    cursor = conn.cursor()

    current_month = datetime.now().month

    # Consultar cumpleaños de clientes
    cursor.execute(
        "SELECT ID,Nombre,Apellido,DNI,RIF,FechaNacimiento,Telefono,Email FROM Clientes WHERE strftime('%m', FechaNacimiento) = ?", (f'{current_month:02}',))
    clients_birthdays = cursor.fetchall()

    # Consultar cumpleaños de propietarios
    cursor.execute(
        "SELECT ID,Nombre,Apellido,DNI,RIF,FechaNacimiento,Telefono,Email FROM Propietarios WHERE strftime('%m', FechaNacimiento) = ?", (f'{current_month:02}',))
    owners_birthdays = cursor.fetchall()

    conn.close()

    # Convertir los resultados a una lista de diccionarios
    birthdays_list = []

    for client in clients_birthdays:
        date_obj = datetime.strptime(client[5], '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d/%m/%Y')
        client_dict = {
            "id": client[0],
            "name": client[1],
            "lastName": client[2],
            "dni": client[3],
            "rif": client[4],
            "birthdate": formatted_date,
            "phone": client[6],
            "email": client[7],
            "type": "Cliente"
        }
        birthdays_list.append(client_dict)

    for owner in owners_birthdays:
        owner_dict = {
            "id": owner[0],
            "name": owner[1],
            "lastName": owner[2],
            "dni": owner[3],
            "rif": owner[4],
            "birthdate": owner[5],
            "phone": owner[6],
            "email": owner[7],
            "type": "Propietario"
        }
        birthdays_list.append(owner_dict)

    return birthdays_list

# Inquilinos


@router.delete("/deleteInquilino/{ID}")
async def delete_inquilino(ID: int):
    conn = create_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM Clientes WHERE ID = ?", (ID,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Inquilino no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(e)}")
    finally:
        cursor.close()
        conn.close()
        
    return {"message": "Inquilino eliminado correctamente"}

@router.get("/getInquilinos")
async def get_inquilinos():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Clientes")
    clients = cursor.fetchall()
    conn.close()

    # Convertir los resultados a una lista de diccionarios
    clients_list = []
    for client in clients:
        date_obj = datetime.strptime(client[5], '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d/%m/%Y')
        client_dict = {
            "id": client[0],
            "name": client[1],
            "lastName": client[2],
            "dni": client[3],
            "rif": client[4],
            "birthdate": formatted_date,
            "phone": client[6],
            "email": client[7]
        }
        clients_list.append(client_dict)

    return clients_list

@router.get("/getInquilino/{id}")
async def get_inquilino_information(id: int):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        # Consulta para obtener la información del inquilino, contratos, inmuebles, y propietarios
        cursor.execute("""
            SELECT 
                C.Nombre AS InquilinoNombre,
                C.Apellido AS InquilinoApellido,
                C.DNI AS InquilinoDNI,
                CO.FechaInicio,
                CO.FechaFin,
                CO.Monto,
                CO.Comision,
                I.Direccion AS InmuebleDireccion,
                P.Nombre AS PropietarioNombre,
                P.Apellido AS PropietarioApellido,
                P.DNI AS PropietarioDNI,
                CO.ID
            FROM 
                Contratos CO
            INNER JOIN 
                Clientes C ON CO.ClienteID = C.ID
            INNER JOIN 
                Inmuebles I ON CO.InmuebleID = I.ID
            INNER JOIN 
                Propietarios P ON I.PropietarioID = P.ID
            WHERE 
                C.ID = ?
        """, (id,))
        
        contratos = cursor.fetchall()

        if not contratos:
            raise HTTPException(status_code=404, detail="Inquilino no encontrado o sin contratos")

        # Formatear la respuesta
        response = []
        for contrato in contratos:
            response.append({
                "InquilinoNombre": contrato[0],
                "InquilinoApellido": contrato[1],
                "InquilinoDNI": contrato[2],
                "FechaInicio": contrato[3],
                "FechaFin": contrato[4],
                "Monto": contrato[5],
                "Comision": contrato[6],
                "InmuebleDireccion": contrato[7],
                "PropietarioNombre": contrato[8],
                "PropietarioApellido": contrato[9],
                "PropietarioDNI": contrato[10],
                "ContratoID": contrato[11]
            })

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()

    
    


@router.post("/addInquilino")
async def add_inquilino(client: Person):
    conn = create_connection()
    cursor = conn.cursor()

    # Verificar si ya existe un cliente con el mismo DNI
    cursor.execute("SELECT * FROM Clientes WHERE DNI = ?", (client.dni,))
    existing_client = cursor.fetchone()

    if existing_client:
        conn.close()
        raise HTTPException(
            status_code=400, detail="Cliente with this DNI already exists")

    cursor.execute("SELECT * FROM Clientes WHERE RIF =?", (client.rif,))
    existing_client_rif = cursor.fetchone()
    if existing_client_rif:
        conn.close()
        raise HTTPException(
            status_code=400, detail="Cliente with this RIF already exists")

    # Insertar nuevo cliente si no existe
    cursor.execute(
        "INSERT INTO Clientes (Nombre, Apellido, DNI, RIF, FechaNacimiento, Telefono, Email) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (client.name, client.lastName, client.dni, client.rif,
         client.birthdate, client.phone, client.email)
    )
    conn.commit()
    conn.close()

    return {"Message": "Inquilino registered"}

# Propietarios


class ImageCedula:
    def __init__(self, id: int):
        self.id = id


MEDIA_DIRECTORY = "./media"


@router.post("/addImagenCedula")
async def add_imagen(id: int = Form(...),  file: UploadFile = File(...)):
    try:
        # Procesar la imagen y los datos de ImageInmueble
        image_cedula = ImageCedula(
            id=id)

        # Crear un nombre de archivo único
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(MEDIA_DIRECTORY, unique_filename)

        # Guardar la imagen en el directorio de medios
        with open(file_path, "wb") as image_file:
            image_file.write(await file.read())
        # Aquí puedes hacer cualquier procesamiento adicional con la imagen guardada
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Propietarios SET ImageCedula=? WHERE ID=?",
            (unique_filename, image_cedula.id)
        )
        conn.commit()
        
        return {
            "id": image_cedula.id,
            "imagen": unique_filename  # Devuelve el nombre del archivo único
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_unique_filename(original_filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:6]  # Genera un UUID único de 6 caracteres
    _, file_extension = os.path.splitext(original_filename)
    return f"{timestamp}_{unique_id}{file_extension}"


@router.put('/editClient/{ID}')
async def edit_client(propietario: Propietarios, ID: int):
    conn = create_connection()
    cursor = conn.cursor()
    update_query = """
    UPDATE Propietarios 
    SET 
        Nombre = ?, 
        Apellido = ?, 
        DNI = ?, 
        RIF = ?, 
        FechaNacimiento = ?, 
        Direccion = ?, 
        CodigoPostal = ?, 
        Telefono = ?, 
        Email = ? 
    WHERE ID = ?
    """
    try:
        cursor.execute(update_query, (
            propietario.name,
            propietario.lastName,
            propietario.dni,
            propietario.rif,
            propietario.birthdate,
            propietario.address,
            propietario.CodePostal,
            propietario.phone,
            propietario.email,
            ID
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    return {"message": "Client updated successfully"}


@router.get("/getClients")
async def get_clients():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Propietarios")
    clients = cursor.fetchall()
    conn.close()

    clients_list = []
    for client in clients:
        imagenCedula = client[10]
        if imagenCedula is None:
            imagenCedula = "No tiene imagen"

        # Intentar parsear la fecha de nacimiento en diferentes formatos
        birthdate = client[5]
        date_formats = ['%Y-%m-%d', '%d/%m/%Y']
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(birthdate, fmt)
                formatted_date = date_obj.strftime('%d/%m/%Y')
                break
            except ValueError:
                continue
        else:
            formatted_date = "Fecha inválida"  # Manejo de error si no se puede parsear la fecha

        client_dict = {
            "id": client[0],
            "name": client[1],
            "lastName": client[2],
            "dni": client[3],
            "rif": client[4],
            "birthdate": formatted_date,
            "address": client[6],
            "codePostal": client[7],
            "phone": client[8],
            "email": client[9],
            "imagenCedula": imagenCedula
        }
        clients_list.append(client_dict)

    return clients_list


@router.get("/getClient/{id}")
async def get_client(id: int):
    conn = create_connection()
    cursor = conn.cursor()

    # Consultar el cliente por ID
    cursor.execute("SELECT * FROM Propietarios WHERE id = ?", (id,))
    client = cursor.fetchone()

    conn.close()

    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    # Convertir el resultado a un diccionario
    date_obj = datetime.strptime(client[5], '%Y-%m-%d')
    formatted_date = date_obj.strftime('%d/%m/%Y')
    client_dict = {
        "id": client[0],
        "name": client[1],
        "lastName": client[2],
        "dni": client[3],
        "rif": client[4],
        "birthdate": formatted_date,
        "address": client[6],
        "codePostal": client[7],
        "phone": client[8],
        "email": client[9]
    }

    return client_dict

@router.delete('/deleteClient/{id}')
async def delete_client(id: int):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Propietarios WHERE ID =?", (id,))
    conn.commit()
    conn.close()
    return {"message": "Client deleted successfully"}



@router.post("/addClient")
async def add_client(client: Propietarios):
    conn = create_connection()
    cursor = conn.cursor()

    # Si no se proporciona RIF, usar el valor de DNI
    if not client.rif:
        client.rif = client.dni

    # Verificar si ya existe un cliente con el mismo DNI
    cursor.execute("SELECT * FROM Propietarios WHERE DNI = ?", (client.dni,))
    existing_client = cursor.fetchone()

    if existing_client:
        conn.close()
        raise HTTPException(
            status_code=400, detail="Propietario with this DNI already exists")

    # Verificar si ya existe un cliente con el mismo RIF
    cursor.execute("SELECT * FROM Propietarios WHERE RIF =?", (client.rif,))
    existing_client_rif = cursor.fetchone()
    if existing_client_rif:
        conn.close()
        raise HTTPException(
            status_code=400, detail="Propietario with this RIF already exists")

    cursor.execute(
        "INSERT INTO Propietarios (Nombre, Apellido, DNI, RIF, FechaNacimiento, Telefono, Email, CodigoPostal, Direccion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (client.name, client.lastName, client.dni, client.rif,
         client.birthdate, client.phone, client.email, client.CodePostal, client.address)
    )
    conn.commit()
    conn.close()

    return {"Message": "Client registered"} 
