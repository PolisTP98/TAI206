# ----------------------------
# | IMPORTACIONES NECESARIAS |
# ----------------------------

import asyncio
import secrets
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials


# ------------------------------------
# | INICIALIZAR INSTANCIA DE FastAPI |
# ------------------------------------

app = FastAPI(
    title = "Examen TAI 2ndo parcial", 
    description = "Isaac Abdiel Sánchez López"
)


# ----------------------
# | BASE DE DATOS FAKE |
# ----------------------

# DEFINIR PACIENTES ESTÁTICOS EN LA API
pacientes = [
    {"id_paciente": 1, "name": "Daniela Lisset Elizalde Ortiz", "age": 21}, 
    {"id_paciente": 2, "name": "Gabriela Martínez Cruz", "age": 23}, 
    {"id_paciente": 3, "name": "Alan David Santiago de Vicente", "age": 22}, 
    {"id_paciente": 4, "name": "Ian David Rodríguez Ruiz", "age": 21}
]

# ASIGNAR ID ÚNICO A CADA CITA MÉDICA
id_artificial = 0

# ALMACENAR CITAS MÉDICAS CREADAS DESDE LA API
lista_citas = []


# ---------------------------------------------
# | PROTEGER ENDPOINTS CRÍTICOS CON HTTPBasic |
# ---------------------------------------------

# INICIALIZAR INSTANCIA DE HTTPBasic
security = HTTPBasic()

# DEFINIR CREDENCIALES PARA UTILIZAR LOS ENDPOINS PROTEGIDOS
def validar_credenciales(credentials: HTTPBasicCredentials = Depends(security)):
    usuario = secrets.compare_digest(credentials.username, "root")
    contrasena = secrets.compare_digest(credentials.password, "1234")

    if not(usuario and contrasena):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Credenciales incorrectas"
        )
    return credentials.username


# ---------------------------------
# | MODELOS DE DATOS CON Pydantic |
# ---------------------------------

# CREAR CITAS MÉDICAS
class CrearCita(BaseModel):
    fecha: date = Field(..., description = "Fecha de la cita en formato YYYY-MM-DD")
    motivo: Optional[str] = Field(None, description = "Motivo de la consulta", max_length = 255)

# PROPORCIONAR INFORMACIÓN DE UNA CITA MÉDICA
class CitaRespuesta(BaseModel):
    id_cita: int
    id_paciente: int
    nombre_paciente: str
    fecha: date
    motivo: Optional[str] = None
    confirmada: bool


# -------------------------
# | FUNCIONES ADICIONALES |
# -------------------------

# GENERAR ID AUTO-INCREMENTAL ÚNICO PARA CADA CITA MÉDICA
def generar_id():
    global id_artificial
    id_artificial += 1
    return id_artificial

# ENCONTRAR CITA MÉDICA MEDIANTE SU ID
def encontrar_cita(id_cita: int):
    for cita in lista_citas:
        if cita["id_cita"] == id_cita:
            return cita
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND, 
        detail = f"No se encontró la cita con ID: {id_cita}"
    )

# DEVOLVER NOMBRE DEL PACIENTE (DE LA BASE DE DATOS DE PACIENTES FAKE) MEDIANTE SU ID
def nombre_paciente(id_paciente: int):
    for paciente in pacientes:
        if id_paciente == paciente["id_paciente"]:
            return paciente["name"]
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND, 
        detail = f"No se encontró el paciente con ID: {id_paciente}"
    )

# VALIDAR FECHA DE LA CITA MAYOR O IGUAL A LA FECHA ACTUAL
def validar_fecha_cita(fecha_cita: date):
    if fecha_cita < date.today():
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT, 
            detail = "La fecha de la cita no puede ser menor a la actual"
        )
    return True

# ESTABLECER LÍMITE MÁXIMO DE 3 CITAS EN UN MISMO DÍA POR PACIENTE
def contar_citas_paciente(id_paciente: int, fecha_cita: date):
    contador = 0
    for cita in lista_citas:
        if cita["id_paciente"] == id_paciente and cita["fecha"] == fecha_cita:
            contador += 1
        if contador == 3:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT, 
                detail = "No se pueden asignar más de 3 citas al paciente el mismo día"
            )
    return True


# -----------------------
# | ENDPOINTS DE LA API |
# -----------------------

# PROBAR CONEXIÓN CON LA API
@app.get("/comprobar_conexion", tags = ["HEALTH_CHECK"])
async def comprobar_conexion():
    return {
        "status": "200", 
        "message": "Conexión establecida"
    }

# CREAR CITA MÉDICA
@app.post("/v1/citas", tags = ["CITAS"], status_code = status.HTTP_201_CREATED)
async def crear_cita(id_paciente: int, cita: CrearCita):
    if validar_fecha_cita(fecha_cita = cita.fecha) and contar_citas_paciente(id_paciente = id_paciente, fecha_cita = cita.fecha):
        nueva_cita = {
            "id_cita": generar_id(), 
            "id_paciente": id_paciente, 
            "nombre_paciente": nombre_paciente(id_paciente = id_paciente), 
            "fecha": cita.fecha, 
            "motivo": cita.motivo
        }

        lista_citas.append(nueva_cita)
    
        return CitaRespuesta(
            id_cita = nueva_cita["id_cita"], 
            id_paciente = nueva_cita["id_paciente"], 
            nombre_paciente = nueva_cita["nombre_paciente"], 
            fecha = nueva_cita["fecha"], 
            motivo = nueva_cita["motivo"], 
            confirmada = False
        )

# OBTENER CITA MÉDICA MEDIANTE SU ID
@app.get("/v1/citas/{id}", tags = ["CITAS"])
async def obtener_cita(id_cita: int):
    cita = encontrar_cita(id_cita)
    return {"Cita encontrada": cita}

# OBTENER LAS CITAS MÉDICAS REGISTRADAS
@app.get("/v1/citas", tags = ["CITAS"])
async def obtener_citas(usuario: str = Depends(validar_credenciales)):
    return {
        "total": len(lista_citas), 
        "data": lista_citas
    }

# CONFIRMAR CITA MÉDICA
@app.put("/v1/citas/{id}", tags = ["CITAS"], status_code = status.HTTP_200_OK)
async def confirmar_cita(id_cita: int):
    cita = encontrar_cita(id_cita)
    cita["confirmada"] = True
    return CitaRespuesta(**cita)

# ELIMINAR CITA MÉDICA
@app.delete("/v1/citas/{id}", tags = ["CITAS"], status_code = status.HTTP_204_NO_CONTENT)
async def eliminar_cita(id_cita: int, usuario: str = Depends(validar_credenciales)):
    cita = encontrar_cita(id_cita)
    lista_citas.pop(cita)
    return {"Cita eliminada": cita}