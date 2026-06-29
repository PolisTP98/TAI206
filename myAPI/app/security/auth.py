# ----------------------------
# | IMPORTACIONES NECESARIAS |
# ----------------------------

import secrets
from fastapi import status, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials


# ----------------------------
# | SEGURIDAD CON HTTP BASIC |
# ----------------------------

# INICIALIZAR LA INSTANCIA CON "HTTPBasic"
security = HTTPBasic()

def verify_request(credentials: HTTPBasicCredentials = Depends(security)):
    auth_user = secrets.compare_digest(credentials.username, "PolisTP98")
    auth_pass = secrets.compare_digest(credentials.password, "PolisTP98")

    if not(auth_user and auth_pass):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid credentials", 
        )
    return credentials.username