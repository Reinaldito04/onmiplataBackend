from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from db.db import create_connection
from models.Auth import LoginCredentials, RegisterUser


router = APIRouter()


@router.post("/login")
async def login(credentials: LoginCredentials):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT Username, Password, Tipo FROM users WHERE Username=? AND Password=?",
                (credentials.username, credentials.password))
    user = cur.fetchone()
    conn.close()
    
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    usuario = user[0]
    tipo = user[2]
    
    return {"message": "Login successful", "username": usuario, "type": tipo}


@router.post("/register")
async def registrar(credentials: RegisterUser):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (Username, Password,Tipo) VALUES (?, ?,?)",
                (credentials.username, credentials.password, credentials.tipo))
    conn.commit()
    conn.close()
    return {"message": "User registered successfully"}
