from fastapi import APIRouter, HTTPException
from db.db import create_connection
from models.Clients import Clients

router = APIRouter()


@router.get("/getClients")
async def get_clients():
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


@router.get("/getClient/{id}")
async def get_client(id: int):
    conn = create_connection()
    cursor = conn.cursor()

    # Consultar el cliente por ID
    cursor.execute("SELECT * FROM Clientes WHERE id = ?", (id,))
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
        "phone": client[6],
        "email": client[7]
    }

    return client_dict


@router.post("/addClient")
async def add_client(client: Clients):
    conn = create_connection()
    cursor = conn.cursor()

    # Verificar si ya existe un cliente con el mismo DNI
    cursor.execute("SELECT * FROM Clientes WHERE DNI = ?", (client.dni,))
    existing_client = cursor.fetchone()

    if existing_client:
        conn.close()
        raise HTTPException(
            status_code=400, detail="Client with this DNI already exists")

    cursor.execute("SELECT * FROM Clientes WHERE RIF =?", (client.rif,))
    existing_client_rif = cursor.fetchone()
    if existing_client_rif:
        conn.close()
        raise HTTPException(
            status_code=400, detail="Client with this RIF already exists")

    # Insertar nuevo cliente si no existe
    cursor.execute(
        "INSERT INTO Clientes (Nombre, Apellido, DNI, RIF, FechaNacimiento, Telefono, Email) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (client.name, client.lastName, client.dni, client.rif,
         client.birthdate, client.phone, client.email)
    )
    conn.commit()
    conn.close()

    return {"Message": "Client registered"}
