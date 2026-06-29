# ----------------------------
# | IMPORTACIONES NECESARIAS |
# ----------------------------

import os 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# ---------------------------------
# | CONEXIÓN CON LA BASE DE DATOS |
# ---------------------------------

# DEFINIR LA URL DE CONEXIÓN
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:123456@postgres:5432/DB_miapi"
)

# CREAR EL MOTOR DE CONEXIÓN 
engine = create_engine(DATABASE_URL)

# AGREGAR EL GESTOR DE CONEXIONES
sesionLocal = sessionmaker(
    autocommit = False, 
    autoflush = False, 
    bind = engine
)

# BASE DECLARATIVA PARA LOS MODELOS
Base = declarative_base() 

# FUNCIÓN PARA EL MANEJO EN SESSION DE LOS REQUEST
def get_db():
    db = sesionLocal()
    try:
        yield db
    finally:
        db.close()