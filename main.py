from fastapi import FastAPI
from routers.users import router as router_users
from routers.clients import router as router_clients
from routers.Inmueble import router as router_inmueble
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


origins = [
    "http://localhost:5173",  # Reemplaza con la URL de tu frontend
    # Agrega otras URLs de frontend si es necesario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router_users)
app.include_router(router_inmueble)
app.include_router(router_clients)


@app.get("/")
async def root():
    return {"message": "Hello World"}