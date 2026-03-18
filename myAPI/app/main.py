# ----------------------------
# | IMPORTACIONES NECESARIAS |
# ----------------------------

from fastapi import FastAPI
from app.routers import users, misc


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