# ----------------------------
# | IMPORTACIONES NECESARIAS |
# ----------------------------

from sqlalchemy import Column, Integer, String
from app.data.db import Base 


# ------------------------------
# | MODELO ORM DE LOS USUARIOS |
# ------------------------------

class user(Base):
    __tablename__ = "users_tb"
    id = Column(Integer, primary_key = True, index = True)
    name = Column(String)
    age = Column(Integer)
    aka = Column(String)