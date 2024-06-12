from fastapi import APIRouter
from pydantic import BaseModel
from db.db import create_connection
from models.Auth import LoginCredentials, RegisterUser


router = APIRouter()


@router.post("/login")
async def login(credentials: LoginCredentials):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE Username=? AND Password=?",
                (credentials.username, credentials.password))
    user = cur.fetchone()
    conn.close()
    return {"message": "Login successful"}


@router.post("/register")
async def registrar(credentials: RegisterUser):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (Username, Password,Tipo) VALUES (?, ?,?)",
                (credentials.username, credentials.password, credentials.tipo))
    conn.commit()
    conn.close()
    return {"message": "User registered successfully"}
