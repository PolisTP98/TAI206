from pydantic import BaseModel, Field

# -----------------------------------
# | MODELO DE VALIDACIÓN "Pydantic" |
# -----------------------------------

class UserBase(BaseModel):
    id: int = Field(..., gt = 0, description = "User identifier", examples = [1])
    name: str = Field(..., min_length = 3, max_length = 255, description = "User name", examples = ["Isaac Abdiel Sánchez López"])
    age: int = Field(..., ge = 0, le = 121, description = "Valid age between 0 and 121", examples = [20])
    aka: str = Field(..., min_length = 3, max_length = 50, description = "User nickname", examples = ["The GOAT"])