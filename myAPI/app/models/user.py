# ----------------------------
# | IMPORTACIONES NECESARIAS |
# ----------------------------

from pydantic import BaseModel, Field
from typing import Optional


# -----------------------------------
# | MODELO DE VALIDACIÓN "Pydantic" |
# -----------------------------------

class UserBase(BaseModel):
    name: str = Field(..., min_length = 3, max_length = 255, description = "User name", examples = ["Isaac Abdiel Sánchez López"])
    age: int = Field(..., ge = 0, le = 121, description = "Valid age between 0 and 121", examples = [20])
    aka: str = Field(..., min_length = 3, max_length = 50, description = "User nickname", examples = ["The GOAT"])


# ---------------------------------------
# | MODELO PARA ACTUALIZACIÓN PARCIAL   |
# ---------------------------------------

class UserPatch(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    aka: Optional[str] = None