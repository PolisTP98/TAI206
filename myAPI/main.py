# -----------------
# | IMPORTACIONES |
# -----------------

from fastapi import FastAPI


# ------------------------
# | INICIALIZAR SERVIDOR |
# ------------------------

app = FastAPI()


# -------------
# | ENDPOINTS |
# -------------

# ENDPOINT PRINCIPAL DE LA API
@app.get("/")
async def helloworld():
    return {"message": "Hello world FastAPI"}

# ENDPOINT "bienvenidos"
@app.get("/welcome_message")
async def welcome_message():
    return {"message": "Welcome to your API REST"}