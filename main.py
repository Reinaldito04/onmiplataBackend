from fastapi import FastAPI
from routers.users import router as router_users
from routers.clients import router as router_clients
from routers.rentals import router as router_rentals
from routers.Inmueble import router as router_inmueble
from routers.Payments import router as router_payments
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers.reports import router as router_reports
from routers.Information import router as router_information
from routers.Legals import router as router_legals
import os 
from fastapi.responses import FileResponse
from fastapi import HTTPException
app = FastAPI()


origins = [
    "http://localhost:5173",  # Reemplaza con la URL de tu frontend
    # Agrega otras URLs de frontend si es necesario
]
app.mount("/media", StaticFiles(directory="media"), name="media")
# Monta la carpeta 'reports/output' para servir archivos estáticos desde '/reports/output'
app.mount("/reports/output", StaticFiles(directory="reports/output"), name="reports_output")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router_users)
app.include_router(router_inmueble)
app.include_router(router_clients)
app.include_router(router_rentals)
app.include_router(router_payments)
app.include_router(router_reports)
app.include_router(router_information)
app.include_router(router_legals)

@app.get("/")
async def root():
    return {"message": "Hello World"}
