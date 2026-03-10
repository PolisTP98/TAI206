import asyncio
import secrets
from typing import Optional
from fastapi import FastAPI, status, HTTPException
from fastapi import FastAPI, status, HTTPException, Depends
from pydantic import BaseModel, Field
import asyncio
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from datetime import datetime

app = FastAPI(
    title = "Examen TAI 2ndo parcial", 
    description = "Isaac Abdiel Sánchez López", 
)

pacientes = [
    {"id_paciente": 1, "name": "Daniela Lisset Elizalde Ortiz", "age": 20}, 
    {"id_paciente": 2, "name": "Gabriela Martínez Cruz", "age": 22}, 
    {"id_paciente": 3, "name": "Alan David Santiago de Vicente", "age": 21}, 
    {"id_paciente": 4, "name": "Ian David Rodríguez Ruiz", "age": 21}
]

security = HTTPBasic()

def verify_request(credentials: HTTPBasicCredentials = Depends(security)):
    usuario = secrets.compare_digest(credentials.username, "root")
    contrasena = secrets.compare_digest(credentials.password, "1234")

    if not(usuario and contrasena):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Credenciales inválidas", 
        )
    return credentials.username

class CrearCita(BaseModel):
    id_cita: int = Field(..., gt = 0, description = "Indentificador de la cita", examples = [1])
    nombre_paciente: str = Field(..., min_length = 5, max_length = 255, description = "Nombre del paciente", examples = ["Isaac Abdiel Sánchez López"])
    fecha: datetime
    motivo: Optional[str] = None

class ConfirmarCita(CrearCita):
    id_cita: int
    confirmada: bool

class EliminarCita(CrearCita):
    id_cita: int
    disponible: bool

lista_de_citas = []

def encontrar_cita(id_cita):
    for cita in lista_de_citas:
        if cita["id_cita"] == id_cita:
            return cita
    return None

def cita_confirmada(id_cita):
    for cita in lista_de_citas:
        if cita["id_cita"] == id_cita:
            return cita["confirmada"]
    
def cita_eliminada(id_cita):
    for cita in lista_de_citas:
        if cita["id_cita"] == id_cita:
            return cita["disponible"]

@app.get("/comprobar_conexion", tags = ["HEALTH_CHECK"])
async def comprobar_conexion():
    return {
        "message": "Conexión establecida", 
        "status": "200"
    }

