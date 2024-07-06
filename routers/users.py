from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.db import create_connection
from models.Auth import LoginCredentials, RegisterUser, registerInformation


router = APIRouter()


@router.get("/getInformationUsers")
async def obtenerinformation():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Registros")
    rows = cur.fetchall()
    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "description": row[1],
            "username": row[2]
        })
    return result


@router.post("/addInformation")
async def registroInformation(data: registerInformation):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Registros (Descripcion,RealizadoPor) values (?,?)",
                (data.description, data.username))
    conn.commit()
    conn.close()
    return {
        "Message": "agregado correctamente"
    }


@router.get("/getUsername")
async def obtenerUser():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT Username,ID FROM users")
    rows = cur.fetchall()
    result = []
    for row in rows:
        result.append({
            "username": row[0],
            "id": row[1]
        })
    return result


@router.post("/login")
async def login(credentials: LoginCredentials):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT Username, Password, Tipo FROM users WHERE Username=? AND Password=?",
                (credentials.username, credentials.password))
    user = cur.fetchone()
    conn.close()

    if user is None:
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    usuario = user[0]
    tipo = user[2]

    return {"message": "Login successful", "username": usuario, "type": tipo}


@router.delete("/deleteUser")
async def delete_user(ID: int):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE ID =?", (ID,))
    conn.commit()
    conn.close()
    return {"message": "User deleted successfully"}


@router.post("/register")
async def registrar(credentials: RegisterUser):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (Username, Password,Tipo) VALUES (?, ?,?)",
                (credentials.username, credentials.password, credentials.tipo))
    conn.commit()
    conn.close()
    return {"message": "User registered successfully"}
