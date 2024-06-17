from fastapi import APIRouter, HTTPException
from db.db import create_connection
from models.Clients import Propietarios, Person
from datetime import datetime

router = APIRouter()

# Cumpleaños
@router.get("/getBirthdays")
async def get_birthdays():
    conn = create_connection()
    cursor = conn.cursor()

    current_month = datetime.now().month

    # Consultar cumpleaños de clientes
    cursor.execute("SELECT ID,Nombre,Apellido,DNI,RIF,FechaNacimiento,Telefono,Email FROM Clientes WHERE strftime('%m', FechaNacimiento) = ?", (f'{current_month:02}',))
    clients_birthdays = cursor.fetchall()

    # Consultar cumpleaños de propietarios
    cursor.execute("SELECT ID,Nombre,Apellido,DNI,RIF,FechaNacimiento,Telefono,Email FROM Propietarios WHERE strftime('%m', FechaNacimiento) = ?", (f'{current_month:02}',))
    owners_birthdays = cursor.fetchall()

    conn.close()

    # Convertir los resultados a una lista de diccionarios
    birthdays_list = []

    for client in clients_birthdays:
        client_dict = {
            "id": client[0],
            "name": client[1],
            "lastName": client[2],
            "dni": client[3],
            "rif": client[4],
            "birthdate": client[5],
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
        client_dict = {
            "id": client[0],
            "name": client[1],
            "lastName": client[2],
            "dni": client[3],
            "rif": client[4],
            "birthdate": client[5],
            "phone": client[6],
            "email": client[7]
        }
        clients_list.append(client_dict)

    return clients_list

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
@router.get("/getClients")
async def get_clients():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Propietarios")
    clients = cursor.fetchall()
    conn.close()

    # Convertir los resultados a una lista de diccionarios
    clients_list = []
    for client in clients:
        client_dict = {
            "id": client[0],
            "name": client[1],
            "lastName": client[2],
            "dni": client[3],
            "rif": client[4],
            "birthdate": client[5],
            "address": client[6],
            "codePostal": client[7],
            "phone": client[8],
            "email": client[9]
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
    client_dict = {
        "id": client[0],
        "name": client[1],
        "lastName": client[2],
        "dni": client[3],
        "rif": client[4],
        "birthdate": client[5],
        "address": client[6],
        "codePostal": client[7],
        "phone": client[8],
        "email": client[9]
    }

    return client_dict

@router.post("/addClient")
async def add_client(client: Propietarios):
    conn = create_connection()
    cursor = conn.cursor()

    # Verificar si ya existe un cliente con el mismo DNI
    cursor.execute("SELECT * FROM Propietarios WHERE DNI = ?", (client.dni,))
    existing_client = cursor.fetchone()

    if existing_client:
        conn.close()
        raise HTTPException(
            status_code=400, detail="Propietario with this DNI already exists")

    cursor.execute("SELECT * FROM Propietarios WHERE RIF =?", (client.rif,))
    existing_client_rif = cursor.fetchone()
    if existing_client_rif:
        conn.close()
        raise HTTPException(
            status_code=400, detail="Propietario with this RIF already exists")

    # Insertar nuevo cliente si no existe
    cursor.execute(
        "INSERT INTO Propietarios (Nombre, Apellido, DNI, RIF, FechaNacimiento, Telefono, Email, CodigoPostal, Direccion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (client.name, client.lastName, client.dni, client.rif,
         client.birthdate, client.phone, client.email, client.CodePostal, client.address)
    )
    conn.commit()
    conn.close()

    return {"Message": "Client registered"}
