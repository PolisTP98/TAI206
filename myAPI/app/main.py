# ----------------------------
# | IMPORTACIONES NECESARIAS |
# ----------------------------

from fastapi import FastAPI
from app.routers import misc, users
from app.data.db import engine
from app.data import user


# ----------------------------
# | BASE DE DATOS AUTOMÁTICA |
# ----------------------------

# CREAR LA TABLA DE USUARIOS AUTOMÁTICAMENTE
user.Base.metadata.create_all(bind = engine)


# --------------------------------------
# | INICIALIZAR LA INSTANCIA DE LA API |
# --------------------------------------

app = FastAPI(
    title = "My first API", 
    description = "Isaac Abdiel Sánchez López", 
    version = "1.0"
)

app.include_router(users.router)
app.include_router(misc.router)