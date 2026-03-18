# ----------------------------
# | IMPORTACIONES NECESARIAS |
# ----------------------------

from fastapi import status, HTTPException, Depends, APIRouter
from app.data.database import users
from app.security.auth import verify_request


# ---------------------------------------
# | INICIALIZAR LA INSTANCIA DEL ROUTER |
# ---------------------------------------

router = APIRouter(
    prefix = "/v1/users", 
    tags = ["USERS_CRUD"]
)


# -------------------------
# | ENDPOINTS DE USUARIOS |
# -------------------------

# ENDPOINT "leer_usuarios" (GET)
@router.get("/")
async def read_users():
    return {
        "status": "200", 
        "total": len(users), 
        "data": users
    }

# ENDPOINT "agregar_usuario" (POST)
@router.post("/")
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
@router.put("/{id}")
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
@router.delete("/{id}")
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