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

id_artificial = 1
lista_de_citas = []

pacientes = [
    {"id_paciente": 1, "name": "Daniela Lisset Elizalde Ortiz", "age": 20}, 
    {"id_paciente": 2, "name": "Gabriela Martínez Cruz", "age": 22}, 
    {"id_paciente": 3, "name": "Alan David Santiago de Vicente", "age": 21}, 
    {"id_paciente": 4, "name": "Ian David Rodríguez Ruiz", "age": 21}
]

security = HTTPBasic()

def validar_credenciales(credentials: HTTPBasicCredentials = Depends(security)):
    usuario = secrets.compare_digest(credentials.username, "root")
    contrasena = secrets.compare_digest(credentials.password, "1234")

    if not(usuario and contrasena):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Credenciales inválidas", 
        )
    return credentials.username

class CrearCita(BaseModel):
    id_paciente: int = Field(gt = 1, ge = len(pacientes))
    fecha: datetime
    motivo: Optional[str] = None

class ConfirmarCita(CrearCita):
    id_cita: int
    confirmada: bool

def generar_id_unico():
    id_artificial += 1 # type: ignore
    return id_artificial

def encontrar_cita(id_cita):
    for cita in lista_de_citas:
        if cita["id_cita"] == id_cita:
            return cita
    return None

def cita_confirmada(id_cita):
    for cita in lista_de_citas:
        if cita["id_cita"] == id_cita:
            return cita["confirmada"]

@app.get("/comprobar_conexion", tags = ["HEALTH_CHECK"])
async def comprobar_conexion():
    return {
        "message": "Conexión establecida", 
        "status": "200"
    }

@app.post("/v1/citas", status_code = status.HTTP_201_CREATED)
async def crear_cita(list_index: int, cita: CrearCita):
    nueva_cita = {
        "id_cita": generar_id_unico(), 
        "id_paciente": pacientes[0]["id_paciente"], 
        "fecha": cita.fecha, 
        "motivo": cita.motivo
    }

    lista_de_citas.append(nueva_cita)

    if nueva_cita["fecha"] >= datetime.now():
        return ConfirmarCita(
            id_cita = nueva_cita["id_cita"], 
            id_paciente = pacientes[list_index]["id_paciente"], 
            fecha = nueva_cita["fecha"], 
            motivo = nueva_cita["motivo"], 
            confirmada = False
        )
    
    raise HTTPException(
        status_code = status.HTTP_409_CONFLICT,
        detail = "La fecha de la cita no puede ser menor a la actual"
    )

@app.get("/v1/citas/{id}", tags = ["CITAS"])
async def obtener_cita(id_cita: int):
    cita = encontrar_cita(id_cita)
    if not cita:
        raise HTTPException(
            status_code = 404, 
            detail = "Cita no encontrada"
        )
    return {"Cita encontrada": cita}

@app.get("/v1/citas", tags = ["CITAS"])
async def obtener_citas(usuario: str = Depends(validar_credenciales)):
    return {
        "status": "200", 
        "total": len(lista_de_citas), 
        "data": lista_de_citas
    }

@app.put("/v1/citas", tags = ["CITAS"], status_code = status.HTTP_200_OK)
async def confirmar_cita(id_cita: int):
    cita = encontrar_cita(id_cita)
    if not cita:
        raise HTTPException(
            status_code = 404, 
            detail = "Cita no encontrada"
        )
    
    cita["confirmada"] = True
    return ConfirmarCita(**cita)

@app.delete("/v1/citas", tags = ["CITAS"], status_code = status.HTTP_204_NO_CONTENT)
async def eliminar_cita(id_cita: int, usuario: str = Depends(validar_credenciales)):
    for index, cita in enumerate(lista_de_citas):
        if cita["id_cita"] == id:
            lista_de_citas.pop(index)
            return
            
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND, 
        detail = f"No se encontró la cita con ID: {id_cita}"
    )