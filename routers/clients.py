from fastapi import APIRouter, HTTPException
from db.db import create_connection
from models.Clients import Propietarios,Person

router = APIRouter()


##Inquilinos 

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

##Propietarios
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
        "INSERT INTO Propietarios (Nombre, Apellido, DNI, RIF, FechaNacimiento, Telefono, Email,CodigoPostal,Direccion) VALUES (?, ?, ?, ?, ?, ?, ?,?,?)",
        (client.name, client.lastName, client.dni, client.rif,
         client.birthdate, client.phone, client.email, client.CodePostal, client.address)
    )
    conn.commit()
    conn.close()

    return {"Message": "Client registered"}
