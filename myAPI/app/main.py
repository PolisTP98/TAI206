# -----------------
# | IMPORTACIONES |
# -----------------

import asyncio
import secrets
from typing import Optional
from fastapi import FastAPI, status, HTTPException, Depends
from pydantic import BaseModel, Field
from fastapi.security import HTTPBasic, HTTPBasicCredentials


# --------------------------------------
# | INICIALIZAR LA INSTANCIA DE LA API |
# --------------------------------------

app = FastAPI(
    title = "My first API", 
    description = "Isaac Abdiel Sánchez López", 
    version = "1.0"
)

# AGREGAR USUARIOS BASE EN LA API
users = [
    {"id": 1, "name": "Daniela Lisset Elizalde Ortiz", "age": 20, "aka": "The most beautiful girl ihesimel"}, 
    {"id": 2, "name": "Gabriela Martínez Cruz", "age": 22, "aka": "My loyal friend"}, 
    {"id": 3, "name": "Alan David Santiago de Vicente", "age": 21, "aka": "The BOMB"},
    {"id": 4, "name": "Ian David Rodríguez Ruiz", "age": 21, "aka": "Straight therian"}
]


# -----------------------------------
# | MODELO DE VALIDACIÓN "Pydantic" |
# -----------------------------------

class UserBase(BaseModel):
    id: int = Field(..., gt = 0, description = "User identifier", examples = [1])
    name: str = Field(..., min_length = 3, max_length = 255, description = "User name", examples = ["Isaac Abdiel Sánchez López"])
    age: int = Field(..., ge = 0, le = 121, description = "Valid age between 0 and 121", examples = [20])
    aka: str = Field(..., min_length = 3, max_length = 50, description = "User nickname", examples = ["The GOAT"])


# ----------------------------
# | SEGURIDAD CON HTTP BASIC |
# ----------------------------

# INICIALIZAR LA INSTANCIA CON "HTTPBasic"
security = HTTPBasic()

def verify_request(credentials: HTTPBasicCredentials = Depends(security)):
    auth_user = secrets.compare_digest(credentials.username, "PolisTP98")
    auth_pass = secrets.compare_digest(credentials.password, "PolisTP98")

    if not(auth_user and auth_pass):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid credentials", 
        )
    return credentials.username


# -------------
# | ENDPOINTS |
# -------------

# ENDPOINT "inicio" (GET)
@app.get("/", tags = ["Start"])
async def hello_world():
    return {"message": "Hello world FastAPI"}

# ENDPOINT "mensaje_de_bienvenida" (GET)
@app.get("/v1/welcome_message", tags = ["Start"])
async def welcome_message():
    return {"message": "Welcome to your API REST"}

# ENDPOINT "calificaciones" (GET)
@app.get("/v1/grades", tags = ["Asynchrony"])
async def grades():
    await asyncio.sleep(5)
    return {"message": "Your grade in TAI is 10"}

# ENDPOINT "usuario" (GET CON PARÁMETRO OBLIGATORIO)
@app.get("/v1/user/{id}", tags = ["Required_parameter"])
async def user(id: int):
    await asyncio.sleep(3)
    return {"user_found": id}

# ENDPOINT "usuario_opcional" (GET CON PARÁMETRO OPCIONAL)
@app.get("/v1/user_optional", tags = ["Optional_parameter"])
async def user_optional(id: Optional[int] = None):
    await asyncio.sleep(3)
    if id is not None:
        for user in users:
            if user["id"] == id:
                return {"user": user}
            return {"message": "User not found"}
    return {"message": "No ID provided"}

# ENDPOINT "leer_usuarios" (GET)
@app.get("/v1/users", tags = ["users_CRUD"])
async def read_users():
    return {
        "status": "200", 
        "total": len(users), 
        "data": users
    }

# ENDPOINT "agregar_usuario" (POST)
@app.post("/v1/users", tags = ["users_CRUD"])
async def add_user(user: dict):
    for user in users:
        if user["id"] == user.get("id"):
            raise HTTPException(
                status_code = 400,
                detail = "User ID already exists"
            )
    users.append(user)
    return {
        "message": "User added succesfully", 
        "data": user, 
        "status": "200"
    }

# ENDPOINT "actualizar_usuario" (PUT)
@app.put("/v1/users/{id}", tags = ["users_CRUD"])
async def update_user(id: int, user_updated: dict):
    for index, usr in enumerate(users):
        if usr["id"] == id:
            # NOS ASEGURAMOS QUE EL ID DEL OBJETO COINCIDA CON EL DE LA URL
            user_updated["id"] = id 
            # REEMPLAZAR EL USUARIO EN LA LISTA
            users[index] = user_updated
            return {
                "message": "User updated succesfully", 
                "data": user_updated
            }
    
    # SI TERMINÓ EL CICLO Y NO ENCONTRÓ NADA
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND, 
        detail = f"User with ID: {id} not found"
    )

# ENDPOINT "eliminar_usuario" (DELETE)
@app.delete("/v1/users/{id}", tags = ["users_CRUD"], status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, auth_user: str = Depends(verify_request)):
    for index, usr in enumerate(users):
        if usr["id"] == id:
            # ELIMINA AL USUARIO DE LA LISTA
            users.pop(index)
            # EN "HTTP_204_NO_CONTENT" NO SE SUELE DEVOLVER body
            return
            
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND, 
        detail = f"User with ID: {id} not found"
    )