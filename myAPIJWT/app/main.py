# -----------------
# | IMPORTACIONES |
# -----------------

import asyncio
import secrets
from typing import Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field


# --------------------------------------
# | INICIALIZAR LA INSTANCIA DE LA API |
# --------------------------------------

app = FastAPI(
    title = "My second API (JWT)", 
    description = "Isaac Abdiel Sánchez López", 
    version = "1.0"
)


# ----------------------------------
# | CONFIGURACIÓN DE SEGURIDAD JWT |
# ----------------------------------

# CLAVE SECRETA PARA FIRMAR LOS TOKENS (SE REEMPLAZA POR UNA VARIABLE DE ENTORNO EN PRODUCCIÓN)
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

# TIEMPO PARA EXPIRACIÓN DE TOKEN (30 MINUTOS)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CONTEXTO PARA HASHEAR LAS CONTRASEÑAS CON bcrypt
pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

# ESQUEMA OAuth2 PARA OBTENER EL TOKEN DE header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")


# --------------------------
# | MODELOS DE DATOS (JWT) |
# --------------------------

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# ------------------------------------
# | BASE DE DATOS DE USUARIOS (Auth) |
# ------------------------------------

# SIMULACIÓN DE USUARIOS PARA AUTENTICACIÓN
fake_users_db = {
    "admin": {
        "username": "admin", 
        "full_name": "Administrator", 
        "email": "admin@example.com", 
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36Tj6cJpGq1p3tZ1pQp1p3t", 
        "disabled": False, 
    }
}

# VERIFICA SI LA CONTRASEÑA EN TEXTO PLANO COINCIDE CON EL HASH
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# GENERA EL HASH DE UNA CONTRASEÑA
def get_password_hash(password):
    return pwd_context.hash(password)

# BUSCA UN USUARIO POR NOMBRE EN LA BASE DE DATOS "fake_users_db"
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return user_dict
    return None

# AUTENTICA UN USUARIO VERIFICANDO SU CONTRASEÑA
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

# CREA UN TOKEN JWT CON TIEMPO DE EXPIRACIÓN
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = 15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt

# DEPENDENCIA PARA OBTENER EL USUARIO ACTUAL A PARTIR DEL TOKEN JWT
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        username: str = payload.get("sub") # type: ignore
        if username is None:
            raise credentials_exception
        token_data = TokenData(username = username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username = token_data.username) # type: ignore
    if user is None:
        raise credentials_exception
    return user


# -----------------------------------
# | MODELO DE VALIDACIÓN "Pydantic" |
# -----------------------------------

class UserBase(BaseModel):
    id: int = Field(..., gt = 0, description = "User identifier", examples = [1])
    name: str = Field(..., min_length = 3, max_length = 255, description = "User name", examples = ["Isaac Abdiel Sánchez López"])
    age: int = Field(..., ge = 0, le = 121, description = "Valid age between 0 and 121", examples = [20])
    aka: str = Field(..., min_length = 3, max_length = 50, description = "User nickname", examples = ["PolisTP98"])


# -----------------------------------------------
# | BASE DE DATOS DE USUARIOS (DATOS DE LA API) |
# -----------------------------------------------

users = [
    {"id": 1, "name": "Daniela Lisset Elizalde Ortiz", "age": 20, "aka": "The most beautiful girl ihesimel"},
    {"id": 2, "name": "Gabriela Martínez Cruz", "age": 22, "aka": "My loyal friend"},
    {"id": 3, "name": "Alan David Santiago de Vicente", "age": 21, "aka": "The BOMB"},
    {"id": 4, "name": "Ian David Rodríguez Ruiz", "age": 21, "aka": "Straight therian"}
]


# -------------
# | ENDPOINTS |
# -------------

# ENDPOINT "inicio" (GET)
@app.get("/", tags = ["START"])
async def hello_world():
    return {"message": "Hello world FastAPI"}

# ENDPOINT "mensaje_de_bienvenida" (GET)
@app.get("/v1/welcome_message", tags = ["START"])
async def welcome_message():
    return {"message": "Welcome to your API REST"}

# ENDPOINT "calificaciones" (GET)
@app.get("/v1/grades", tags = ["ASYNCHRONY"])
async def grades():
    await asyncio.sleep(5)
    return {"message": "Your grade in TAI is 10"}

# ENDPOINT "usuario" (GET CON PARÁMETRO OBLIGATORIO)
@app.get("/v1/user/{id}", tags = ["REQUIRED_PARAMETER"])
async def user(id: int):
    await asyncio.sleep(3)
    return {"user_found": id}

# ENDPOINT "usuario_opcional" (GET CON PARÁMETRO OPCIONAL)
@app.get("/v1/user_optional", tags = ["OPTIONAL_PARAMETER"])
async def user_optional(id: Optional[int] = None):
    await asyncio.sleep(3)
    if id is not None:
        for user in users:
            if user["id"] == id:
                return {"user": user}
            return {"message": "User not found"}
    return {"message": "No ID provided"}

# ENDPOINT "leer_usuarios" (GET)
@app.get("/v1/users", tags = ["USERS_CRUD"])
async def read_users():
    return {
        "status": "200", 
        "total": len(users), 
        "data": users
    }

# ENDPOINT "agregar_usuario" (POST)
@app.post("/v1/users", tags = ["USERS_CRUD"])
async def add_user(user: dict):
    for usr in users:
        if usr["id"] == user.get("id"):
            raise HTTPException(
                status_code = 400, 
                detail = "User ID already exists"
            )
    users.append(user)
    return {
        "message": "User added successfully", 
        "data": user, 
        "status": "200"
    }

# ENDPOINT "actualizar_usuario" (PUT, JWT)
@app.put("/v1/users/{id}", tags = ["USERS_CRUD"])
async def update_user(id: int, user_updated: dict, current_user: dict = Depends(get_current_user)):
    for index, usr in enumerate(users):
        if usr["id"] == id:
            # NOS ASEGURAMOS QUE EL ID DEL OBJETO COINCIDA CON EL DE LA URL
            user_updated["id"] = id
            # REEMPLAZAR EL USUARIO EN LA LISTA
            users[index] = user_updated
            return {
                "message": "User updated successfully", 
                "data": user_updated
            }

    # SI TERMINÓ EL CICLO Y NO ENCONTRÓ NADA
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = f"User with ID: {id} not found"
    )

# ENDPOINT "eliminar_usuario" (DELETE, JWT)
@app.delete("/v1/users/{id}", tags = ["USERS_CRUD"], status_code = status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, current_user: dict = Depends(get_current_user)):
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

# ENDPOINT "token" (OBTENER EL JWT)
@app.post("/token", response_model = Token, tags = ["SECURITY_JWT"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Incorrect username or password", 
            headers = {"WWW-Authenticate": "Bearer"}, 
        )
    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data = {"sub": user["username"]}, 
        expires_delta = access_token_expires
    )
    return {"access_token": access_token, 
            "token_type": "bearer"}