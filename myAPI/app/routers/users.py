# ----------------------------
# | IMPORTACIONES NECESARIAS |
# ----------------------------

from fastapi import status, HTTPException, Depends, APIRouter
from starlette.routing import Route
from app.models.user import UserBase, UserPatch
from app.security.auth import verify_request
from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data.user import user as user_db


# ---------------------------------------
# | INICIALIZAR LA INSTANCIA DEL ROUTER |
# ---------------------------------------

router = APIRouter(
    prefix="/v1/users",
    tags=["USERS_CRUD"]
)


# -------------------------
# | ENDPOINTS DE USUARIOS |
# -------------------------

# ENDPOINT "leer_usuarios" (GET)
@router.get("/")
async def read_users(db: Session = Depends(get_db)):
    consult_users = db.query(user_db).all()
    return {
        "status": "200",
        "total": len(consult_users),
        "data": consult_users
    }

# ENDPOINT "leer_usuarios por ID" (GET)
@router.get("/{id}")
async def get_user_by_id(id: int, db: Session = Depends(get_db)):
    consult_user = db.query(user_db).filter(user_db.id == id).first()
    if consult_user is None:
        raise HTTPException(status_code=404, detail=f"User with ID {id} not found")
    
    return {
        "status": "200",
        "data": consult_user
    }

# ENDPOINT "agregar_usuario" (POST)
@router.post("/")
async def add_user(user: UserBase, db: Session = Depends(get_db)):
    new_user = user_db(name=user.name, age=user.age, aka=user.aka)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Usuario creado correctamente",
        "data": new_user,
        "status": "200"
    }

# ENDPOINT "actualizar_usuario_completo" (PUT)
@router.put("/{id}")
async def update_user(id: int, user_updated: UserBase, db: Session = Depends(get_db)):
    # Buscar el usuario en la base de datos
    db_user = db.query(user_db).filter(user_db.id == id).first()
    if db_user is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"User with ID: {id} not found"
        )

    # Actualizar todos los campos
    db_user.name = user_updated.name # type: ignore
    db_user.age = user_updated.age # type: ignore
    db_user.aka = user_updated.aka # type: ignore

    db.commit()
    db.refresh(db_user)

    return {
        "message": "User updated successfully",
        "data": db_user
    }

# ENDPOINT "actualizar_usuario_parcial" (PATCH)
@router.patch("/{id}")
async def patch_user(id: int, user_patch: UserPatch, db: Session = Depends(get_db)):
    # Buscar el usuario
    db_user = db.query(user_db).filter(user_db.id == id).first()
    if db_user is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"User with ID: {id} not found"
        )

    # Actualizar solo los campos que vienen en el body
    update_data = user_patch.dict(exclude_unset = True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)

    return {
        "message": "User partially updated successfully",
        "data": db_user,
        "status": "200"
    }

# ENDPOINT "eliminar_usuario" (DELETE)
@router.delete("/{id}")
async def delete_user(id: int, auth_user: str = Depends(verify_request), db: Session = Depends(get_db)):
    # Buscar el usuario
    db_user = db.query(user_db).filter(user_db.id == id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID: {id} not found"
        )

    # Eliminar de la base de datos
    db.delete(db_user)
    db.commit()

    # Código 204 sin contenido
    return