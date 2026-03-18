# ----------------------------
# | IMPORTACIONES NECESARIAS |
# ----------------------------

import asyncio
from typing import Optional
from fastapi import APIRouter
from app.data.database import users


# ---------------------------------------
# | INICIALIZAR LA INSTANCIA DEL ROUTER |
# ---------------------------------------

router = APIRouter(
    tags = ["MISCELANIUS"]
)


# -------------------------
# | ENDPOINTS ADICIONALES |
# -------------------------

# ENDPOINT "inicio" (GET)
@router.get("/", tags = ["Start"])
async def hello_world():
    return {"message": "Hello world FastAPI"}

# ENDPOINT "mensaje_de_bienvenida" (GET)
@router.get("/v1/welcome_message", tags = ["Start"])
async def welcome_message():
    return {"message": "Welcome to your API REST"}
    
# ENDPOINT "usuario" (GET CON PARÁMETRO OBLIGATORIO)
@router.get("/v1/user/{id}")
async def user(id: int):
    await asyncio.sleep(3)
    return {"user_found": id}

# ENDPOINT "usuario_opcional" (GET CON PARÁMETRO OPCIONAL)
@router.get("/v1/user_optional", tags = ["Optional_parameter"])
async def user_optional(id: Optional[int] = None):
    await asyncio.sleep(3)
    if id is not None:
        for user in users:
            if user["id"] == id:
                return {"user": user}
            return {"message": "User not found"}
    return {"message": "No ID provided"}

# ENDPOINT "calificaciones" (GET)
@router.get("/v1/grades", tags = ["Asynchrony"])
async def grades():
    await asyncio.sleep(5)
    return {"message": "Your grade in TAI is 10"}